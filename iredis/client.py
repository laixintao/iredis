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

    ANSWER_CALLBACKS = {"HGETALL": renders.render_dict}

    def __init__(self, h, p, n):
        self.host = h
        self.port = p
        self.db = n
        self._redis_client = redis.StrictRedis(
            self.host, self.port, self.db, decode_responses=True
        )
        self.connection = Connection()
        self.answer_callbacks = {}

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
        except ResponseError:
            # only print response error
            raise
        # TODO
        # resp callback
        return response

    def send_command(self, command):
        # FIXME args include ", strip it
        # multi key: "123" "foo" "bar"
        # \" : "fo\"o"
        # space
        redis_commands = command.split(" ")
        logger.debug(f"[comamnd list] {redis_commands}")
        redis_resp = self.execute_command(*redis_commands)
        # FIXME command name can not only split by " "
        # command name include " "
        # for key in variables:
        #   key.starts_with command_*  then it is command
        command_name = redis_commands[0]
        if command_name in self.answer_callbacks:
            rendered = self.answer_callbacks[command_name](redis_resp)
        else:
            rendered = redis_resp
        return redis_resp
