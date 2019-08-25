"""
IRedis client.
"""
import logging

from redis.connection import Connection
from redis.exceptions import ResponseError, TimeoutError, ConnectionError

from . import renders
from .commands_csv_loader import all_commands, command2callback
from .utils import nativestr, split_command_args

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

    def execute_command(self, completer, command_name, *args, **options):
        "Execute a command and return a parsed response"
        # === pre hook ===
        if command_name.upper() == "SELECT":
            logger.debug("[Pre hook] Command is SELECT, change self.db.")
            self.db = int(args[0])

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
        # === After hook ===
        # SELECT db on AUTH
        if command_name.upper() == "AUTH" and self.db:
            select_result = self.execute_command(completer, "SELECT", self.db)
            if nativestr(select_result) != "OK":
                raise ConnectionError("Invalid Database")

        return resp

    def parse_response(self, connection, completer, command_name, **options):
        "Parses a response from the Redis server"
        try:
            response = connection.read_response()
            logger.info(f"[Redis-Server] Response: {response}")
        except ResponseError as e:
            logger.warn(f"[Redis-Server] ERROR: {str(e)}")
            response = str(e)
        command_upper = command_name.upper()
        if (
            command_upper in self.answer_callbacks
            and self.answer_callbacks[command_upper]
        ):
            callback_name = self.answer_callbacks[command_upper]
            callback = self.callbacks[callback_name]
            rendered = callback(response, completer)
        else:
            rendered = response
        logger.info(f"[rendered] {rendered}")
        return rendered

    def parse_input(self, input_command):
        """
        parse input command to command and args.
        convert input to upper case, we use upper case command internally;
        strip quotes in args
        """
        return None

    def send_command(self, command, completer):
        """
        Send command to redis-server, return parsed response.

        :param command: text command, not parsed
        :param completer: RedisGrammarCompleter will update completer
            based on redis response. eg: update key completer after ``keys``
            command
        """
        input_command, args = split_command_args(command, all_commands)
        redis_resp = self.execute_command(completer, input_command, *args)
        return redis_resp
