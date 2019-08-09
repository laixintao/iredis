"""
Redis client.
"""
import logging

import redis

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, h, p, n):
        self.host = h
        self.port = p
        self.db = n
        self._redis_client = redis.StrictRedis(
            self.host, self.port, self.db, decode_responses=True
        )

    def __str__(self):
        return f"{self.host}:{self.port}[{self.db}]> "

    def send_command(self, command):
        redis_commands = command.split(" ")
        logger.debug(f"[Redis split comamnd] {redis_commands}")
        return self._redis_client.execute_command(*redis_commands)
