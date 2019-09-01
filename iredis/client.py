"""
IRedis client.
"""
import logging

import redis
from redis.connection import Connection
from redis.exceptions import TimeoutError, ConnectionError

from . import renders
from .config import config
from .commands_csv_loader import all_commands, command2callback
from .utils import nativestr, split_command_args, _strip_quote_args
from .renders import render_error

logger = logging.getLogger(__name__)


class Client:
    """
    iRedis client, hold a redis-py Client to interact with Redis.
    """

    def reder_funcname_mapping(self):
        mapping = {}
        for func_name, func in renders.__dict__.items():
            if callable(func):
                mapping[func_name] = func
        return mapping

    def __init__(self, host, port, db, password=None, encoding=None):
        self.host = host
        self.port = port
        self.db = db
        if encoding:
            self.connection = Connection(
                host=self.host,
                port=self.port,
                db=self.db,
                password=password,
                encoding=encoding,
                decode_responses=True,
                encoding_errors="replace",
            )
        else:
            self.connection = Connection(
                host=self.host,
                port=self.port,
                db=self.db,
                password=password,
                decode_responses=False,
            )
        # all command upper case
        self.answer_callbacks = command2callback
        self.callbacks = self.reder_funcname_mapping()

    def __str__(self):
        if self.db:
            return f"{self.host}:{self.port}[{self.db}]"
        return f"{self.host}:{self.port}"

    def execute_command_and_read_response(self, completer, command_name, *args, **options):
        "Execute a command and return a parsed response"
        # === pre hook ===
        # TRANSATION state chage
        if command_name.upper() in ["EXEC", "DISCARD"]:
            logger.debug(f"[After hook] Command is {command_name}, unset transaction.")
            config.transaction = False

        try:
            self.connection.send_command(command_name, *args)
            resp = self.parse_response(
                self.connection, completer, command_name, **options
            )
        # retry on timeout
        except (ConnectionError, TimeoutError) as e:
            self.connection.disconnect()
            if not (self.connection.retry_on_timeout and isinstance(e, TimeoutError)):
                raise
            self.connection.send_command(command_name, *args)
            resp = self.parse_response(
                self.connection, completer, command_name, **options
            )
        except redis.exceptions.ExecAbortError:
            config.transaction = False
            raise

        # === After hook ===
        # SELECT db on AUTH
        if command_name.upper() == "AUTH" and self.db:
            select_result = self.execute_command_and_read_response(completer, "SELECT", self.db)
            if nativestr(select_result) != "OK":
                raise ConnectionError("Invalid Database")
        elif command_name.upper() == "SELECT":
            logger.debug("[After hook] Command is SELECT, change self.db.")
            self.db = int(args[0])
        if command_name.upper() == "MULTI":
            logger.debug("[After hook] Command is MULTI, start transaction.")
            config.transaction = True

        return resp

    def render_command_result(self, command_name, response, completer):
        """
        Render command result using callback

        :param command_name: command name, (will be converted
            to UPPER case;
        :param completer: completers to be patched;
        """
        command_upper = command_name.upper()
        # else, use defined callback
        if (
            command_upper in self.answer_callbacks
            and self.answer_callbacks[command_upper]
        ):
            callback_name = self.answer_callbacks[command_upper]
            callback = self.callbacks[callback_name]
            rendered = callback(response, completer)
        # FIXME
        # not implemented command, use no transaction
        # this `else` should be deleted finally
        else:
            rendered = response
        logger.info(f"[rendered] {rendered}")
        return rendered

    def parse_response(self, connection, completer, command_name, **options):
        "Parses a response from the Redis server"
        response = connection.read_response()
        logger.info(f"[Redis-Server] Response: {response}")
        # if in transaction, use queue render first
        if config.transaction:
            callback = renders.render_transaction_queue
            rendered = callback(response, completer)
        else:
            rendered = self.render_command_result(command_name, response, completer)
        return rendered

    def send_command(self, command, completer):
        """
        Send command to redis-server, return parsed response.

        :param command: text command, not parsed
        :param completer: RedisGrammarCompleter will update completer
            based on redis response. eg: update key completer after ``keys``
            command
        """
        input_command = ""
        try:
            input_command, args = split_command_args(command, all_commands)
            self.patch_completers(command, completer)
            redis_resp = self.execute_command_and_read_response(completer, input_command, *args)
        except Exception as e:
            logger.exception(e)
            return render_error(str(e))

        return redis_resp

    def patch_completers(self, command, completer):
        """
        Before execute command, patch completers first.
        Eg: When user run `GET foo`, key completer need to
          touch foo.

        Only works when compile-grammar thread is done.
        """
        if not completer:
            logger.warning("[Pre patch completer] Complter not ready, not patched...")
            return
        redis_grammar = completer.compiled_grammar
        m = redis_grammar.match(command)
        if not m:
            # invalide command!
            return
        variables = m.variables()
        # parse keys
        keys_token = variables.getall("keys")
        if keys_token:
            for key in _strip_quote_args(keys_token):
                completer.completers["key"].touch(key)
        key_token = variables.getall("key")
        if key_token:
            # NOTE variables.getall will always be a list
            for single_key in _strip_quote_args(key_token):
                completer.completers["key"].touch(single_key)
        logger.debug(f"[Complter key] Done: {completer.completers['key'].words}")
