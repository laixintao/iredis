"""
IRedis client.
"""
import os
from pathlib import Path
import logging

import redis
from redis.connection import Connection
from redis.exceptions import TimeoutError, ConnectionError
from prompt_toolkit.formatted_text import FormattedText

from . import renders
from .config import config
from .commands_csv_loader import all_commands, command2callback, commands_summary
from .utils import nativestr, split_command_args, _strip_quote_args
from .renders import render_error
from .completers import LatestUsedFirstWordCompleter
from . import markdown
from .utils import compose_command_syntax

project_path = Path(os.path.dirname(os.path.abspath(__file__))) / "data"
logger = logging.getLogger(__name__)
CLIENT_COMMANDS = ["HELP"]


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

    def client_execute_command(self, command_name, *args):
        command = command_name.upper()
        if command == "HELP":
            return self.do_help(*args)

    def execute_command_and_read_response(
        self, completer, command_name, *args, **options
    ):
        "Execute a command and return a parsed response"
        # === pre hook ===
        # TRANSATION state chage
        if command_name.upper() in ["EXEC", "DISCARD"]:
            logger.debug(f"[After hook] Command is {command_name}, unset transaction.")
            config.transaction = False
        if command_name.upper() in ["ZSCAN", "ZPOPMAX", "ZPOPMIN"]:
            config.withscores = True

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
            select_result = self.execute_command_and_read_response(
                completer, "SELECT", self.db
            )
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
            # if command is not supposed to send to server
            if input_command.upper() in CLIENT_COMMANDS:
                redis_resp = self.client_execute_command(input_command, *args)
                return redis_resp
            self.pre_hook(command, completer)
            redis_resp = self.execute_command_and_read_response(
                completer, input_command, *args
            )
        except Exception as e:
            logger.exception(e)
            return render_error(str(e))
        finally:
            config.withscores = False
        return redis_resp

    def pre_hook(self, command, completer):
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
        # zset withscores
        withscores = variables.get("withscores")
        logger.debug(f"[PRE HOOK] withscores: {withscores}")
        if withscores:
            config.withscores = True

        # auto update LatestUsedFirstWordCompleter
        for _token, _completer in completer.completers.items():
            if not isinstance(_completer, LatestUsedFirstWordCompleter):
                continue
            # getall always returns a []
            tokens_in_command = variables.getall(_token)
            for tokens_in_command in tokens_in_command:
                # prompt_toolkit didn't support multi tokens
                # like DEL key1 key2 key3
                # so we have to split them manualy
                for single_token in _strip_quote_args(tokens_in_command):
                    _completer.touch(single_token)
            logger.debug(f"[Complter {_token} updated] Done: {_completer.words}")

    def do_help(self, *args):
        command_docs_name = "-".join(args).lower()
        command_summary_name = " ".join(args).upper()
        with open(project_path / "docs" / f"{command_docs_name}.md") as doc_file:
            doc = doc_file.read()
            rendered_detail = markdown.render(doc)
        summary_dict = commands_summary[command_summary_name]
        summary = [
            ("", "\n"),
            ("class:doccommand", "  " + command_summary_name),
            ("", "\n"),
            ("class:dockey", "  summary: "),
            ("", summary_dict["summary"]),
            ("", "\n"),
            ("class:dockey", "  complexity: "),
            ("", summary_dict["complexity"]),
            ("", "\n"),
            ("class:dockey", "  since: "),
            ("", summary_dict["since"]),
            ("", "\n"),
            ("class:dockey", "  group: "),
            ("", summary_dict["group"]),
            ("", "\n"),
            ("class:dockey", "  syntax: "),
            ("", command_summary_name),  # command
            *compose_command_syntax(summary_dict, style_class=""),  # command args
            ("", "\n\n"),
        ]

        return FormattedText(summary + rendered_detail)
