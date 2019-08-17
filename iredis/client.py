"""
IRedis client.
"""
import re
import logging

import redis
from redis.connection import Connection
from redis.exceptions import ResponseError, TimeoutError, ConnectionError
from iredis.exceptions import InvalidArguments

from . import renders
from .commands_csv_loader import all_commands

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
        if self.db:
            return f"{self.host}:{self.port}[{self.db}]"
        return f"{self.host}:{self.port}"

    def execute_command(self, command_name, *args, **options):
        "Execute a command and return a parsed response"
        # TODO if command is auth and n is not None
        # need to SELECT after auth
        try:
            self.connection.send_command(command_name, *args)
            return self.parse_response(self.connection, command_name, **options)
        except (ConnectionError, TimeoutError) as e:
            self.connection.disconnect()
            if not (self.connection.retry_on_timeout and isinstance(e, TimeoutError)):
                raise
            self.connection.send_command(command_name, *args)
            return self.parse_response(self.connection, command_name, **options)

    def parse_response(self, connection, command_name, **options):
        "Parses a response from the Redis server"
        try:
            response = connection.read_response()
        except ResponseError as e:
            rendered = str(e)
        else:
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

    def _valide_token(self, words):
        token = "".join(words).strip()
        if token:
            yield token

    def _strip_quote_args(self, s):
        """
        Given string s, split it into args.(Like bash paring)
        Handle with all quote cases.

        Raise ``InvalidArguments`` if quotes not match

        :return: args list.
        """
        sperator = re.compile(r"\s")
        word = []
        in_quote = None
        pre_back_slash = False
        for char in s:
            if in_quote:
                # close quote
                if char == in_quote:
                    if not pre_back_slash:
                        yield from self._valide_token(word)
                        word = []
                        in_quote = None
                    else:
                        # previous char is \ , merge with current "
                        word[-1] = char
                else:
                    word.append(char)
            # not in quote
            else:
                # sperator
                if sperator.match(char):
                    if word:
                        yield from self._valide_token(word)
                        word = []
                    else:
                        word.append(char)
                # open quotes
                elif char in ["'", '"']:
                    in_quote = char
                else:
                    word.append(char)
            if char == "\\" and not pre_back_slash:
                pre_back_slash = True
            else:
                pre_back_slash = False

        if word:
            yield from self._valide_token(word)
        # quote not close
        if in_quote:
            raise InvalidArguments()

    def send_command(self, command):
        """
        Send command to redis-server, return parsed response.
        """

        # Parse command-name and args
        upper_raw_command = command.upper()
        for command_name in all_commands:
            if upper_raw_command.startswith(command_name):
                l = len(command_name)
                input_command = command[:l]
                input_args = command[l:]
                break
        else:
            raise InvalidArguments(r"`{command} is not a valide Redis Command")

        args = list(self._strip_quote_args(input_args))

        logger.debug(f"[Parsed comamnd name] {input_command}")
        logger.debug(f"[Parsed comamnd args] {args}")
        redis_resp = self.execute_command(input_command, *args)
        return redis_resp
