"""
Redis client.
"""
import logging

import redis
from redis.connection import Connection
from redis.exceptions import ResponseError, TimeoutError, ConnectionError

from . import renders

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

    def __init__(self, h, p, n):
        self.host = h
        self.port = p
        self.db = n
        self._redis_client = redis.StrictRedis(
            self.host, self.port, self.db, decode_responses=True
        )
        self.connection = Connection()
        self.answer_callbacks = {"KEYS": "render_int"}
        self.callbacks = self.reder_funcname_mapping()

    def __str__(self):
        return f"{self.host}:{self.port}[{self.db}]"

    def execute_command(self, *args, **options):
        "Execute a command and return a parsed response"
        command_name = args[0]
        try:
            self.connection.send_command(*args)
            return self.parse_response(self.connection, command_name, **options)
        except (ConnectionError, TimeoutError) as e:
            self.connection.disconnect()
            if not (self.connection.retry_on_timeout and isinstance(e, TimeoutError)):
                raise
            self.connection.send_command(*args)
            return self.parse_response(self.connection, command_name, **options)

    def parse_response(self, connection, command_name, **options):
        "Parses a response from the Redis server"
        try:
            response = connection.read_response()
        except ResponseError as e:
            rendered = str(e)
        else:
            # FIXME command name can not only split by " "
            # command name include " "
            # for key in variables:
            #   key.starts_with command_*  then it is command
            if command_name in self.answer_callbacks:
                callback_name = self.answer_callbacks[command_name]
                callback = self.callbacks[callback_name]
                rendered = callback(response)
            else:
                rendered = response
        return rendered

    def parse_input(self, input_command):
        """
        parse input command to command and args.
        convert input to upper case, we use upper case command internally;
        strip quotes in args
        """
        return None

    def _strip_quotes(self, s):
        """

        Raise Error if quotes not match
        """
        for char in s:
            pass


    def send_command(self, command):
        # FIXME args include ", strip it
        # multi key: "123" "foo" "bar"
        # \" : "fo\"o"
        # space
        redis_commands = command.split(" ")
        logger.debug(f"[comamnd list] {redis_commands}")
        redis_resp = self.execute_command(*redis_commands)
        return redis_resp
