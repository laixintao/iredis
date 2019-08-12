"""
Redis client.
"""
import logging

import redis
from redis.client import CaseInsensitiveDict

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
        self.answer_callbacks = CaseInsensitiveDict(self.__class__.ANSWER_CALLBACKS)

    def __str__(self):
        return f"{self.host}:{self.port}[{self.db}]"

    def send_command(self, command):
        redis_commands = command.split(" ")
        logger.debug(f"[comamnd list] {redis_commands}")
        redis_resp = self._redis_client.execute_command(*redis_commands)
        # FIXME command name
        command_name = redis_commands[0]
        if command_name in self.answer_callbacks:
            rendered = self.answer_callbacks[command_name](redis_resp)
        else:
            rendered = redis_resp
        return redis_resp
