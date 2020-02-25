"""
IRedis client.
"""
import logging
import re
import sys
from distutils.version import StrictVersion
from importlib_resources import read_text
from subprocess import run

import redis
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import clear
from redis.connection import Connection
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError

from . import markdown, renders
from .data import commands as commands_data
from .commands_csv_loader import (
    all_commands,
    command2callback,
    commands_summary,
    groups,
)
from .completers import IRedisCompleter
from .config import config
from .exceptions import NotRedisCommand
from .renders import OutputRender
from .utils import compose_command_syntax, nativestr, split_command_args, exit
from .warning import confirm_dangerous_command

logger = logging.getLogger(__name__)
CLIENT_COMMANDS = groups["iredis"]


class Client:
    """
    iRedis client, hold a redis-py Client to interact with Redis.
    """

    def __init__(self, host, port, db, password=None):
        self.host = host
        self.port = port
        self.db = db
        if config.decode:
            self.connection = Connection(
                host=self.host,
                port=self.port,
                db=self.db,
                password=password,
                encoding=config.decode,
                decode_responses=True,
                encoding_errors="replace",
                socket_keepalive=config.socket_keepalive,
            )
        else:
            self.connection = Connection(
                host=self.host,
                port=self.port,
                db=self.db,
                password=password,
                decode_responses=False,
                socket_keepalive=config.socket_keepalive,
            )
        # all command upper case
        self.answer_callbacks = command2callback
        try:
            self.connection.connect()
        except Exception as e:
            print(str(e), file=sys.stderr)
        if not config.no_info:
            try:
                self.get_server_info()
            except Exception as e:
                logger.warning(f"[After Connection] {str(e)}")
                config.no_version_reason = str(e)
        else:
            config.no_version_reason = "--no-info flag activated"

    def get_server_info(self):
        # safe to decode Redis's INFO response
        info_resp = nativestr(self.execute("INFO"))
        version = re.findall(r"^redis_version:([\d\.]+)\r\n", info_resp, re.MULTILINE)[
            0
        ]
        logger.debug(f"[Redis Version] {version}")
        config.version = version

    def __str__(self):
        if self.db:
            return f"{self.host}:{self.port}[{self.db}]"
        return f"{self.host}:{self.port}"

    def client_execute_command(self, command_name, *args):
        command = command_name.upper()
        if command == "HELP":
            yield self.do_help(*args)
        if command == "PEEK":
            yield from self.do_peek(*args)
        if command == "CLEAR":
            clear()
        if command == "EXIT":
            exit()

    def execute(self, command_name, *args, **options):
        """Execute a command and return a parsed response
        Here we retry once for ConnectionError.
        """
        retry_times = config.retry_times  # FIXME configureable
        last_error = None
        need_refresh_connection = False

        while retry_times >= 0:
            try:
                if need_refresh_connection:
                    print(
                        f"{str(last_error)} retrying... retry left: {retry_times+1}",
                        file=sys.stderr,
                    )
                    self.connection.disconnect()
                    self.connection.connect()
                    logger.info(f"New connection created, retry on {self.connection}.")
                self.connection.send_command(command_name, *args)
                response = self.connection.read_response()
            except AuthenticationError:
                raise
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Connection Error, got {e}, retrying...")
                last_error = e
                retry_times -= 1
                need_refresh_connection = True

            except redis.exceptions.ExecAbortError:
                config.transaction = False
                raise
            else:
                return response
        raise last_error

    def _dynamic_render(self, command_name, response):
        """
        Render command result using callback

        :param command_name: command name, (will be converted
            to UPPER case;
        """
        return OutputRender.dynamic_render(command_name=command_name, response=response)

    def render_response(self, response, command_name):
        "Parses a response from the Redis server"
        logger.info(f"[Redis-Server] Response: {response}")
        # if in transaction, use queue render first
        if config.transaction:
            callback = renders.OutputRender.render_transaction_queue
            rendered = callback(response)
        else:
            rendered = self._dynamic_render(command_name, response)
        return rendered

    def monitor(self):
        """Redis' MONITOR command:
        https://redis.io/commands/monitor
        This command need to read from a stream resp, so
        it's different
        """
        while 1:
            response = self.connection.read_response()
            yield OutputRender.render_bulk_string_decode(response)

    def subscribing(self):
        while 1:
            response = self.connection.read_response()
            yield OutputRender.render_subscribe(response)

    def unsubscribing(self):
        "unsubscribe from all channels"
        response = self.execute("UNSUBSCRIBE")
        yield OutputRender.render_subscribe(response)

    def split_command_and_pipeline(self, rawinput, completer: IRedisCompleter):
        """
        split user raw input to redis command and shell pipeline.
        eg:
        GET json | jq .key
        return: GET json, jq . key
        """
        grammar = completer.get_completer(input_text=rawinput).compiled_grammar
        matched = grammar.match(rawinput)
        if not matched:
            # invalide command!
            return rawinput, None
        variables = matched.variables()
        shell_command = variables.get("shellcommand")
        if shell_command:
            redis_command = rawinput.replace(shell_command, "")
            shell_command = shell_command.lstrip("| ")
            return redis_command, shell_command
        return rawinput, None

    def send_command(self, raw_command, completer=None):  # noqa
        """
        Send raw_command to redis-server, return parsed response.

        :param raw_command: text raw_command, not parsed
        :param completer: RedisGrammarCompleter will update completer
            based on redis response. eg: update key completer after ``keys``
            raw_command
        """
        if completer is None:  # not in a tty
            redis_command, shell_command = raw_command, None
        else:
            redis_command, shell_command = self.split_command_and_pipeline(
                raw_command, completer
            )
        logger.info(f"[Prepare command] Redis: {redis_command}, Shell: {shell_command}")
        try:
            command_name, args = split_command_args(redis_command, all_commands)
            logger.info(f"[Split command] command: {command_name}, args: {args}")
            input_command_upper = command_name.upper()
            # Confirm for dangerous command
            if config.warning:
                confirm = confirm_dangerous_command(input_command_upper)
                # if we can prompt to user, it's always a tty
                # so we always yield FormattedText here.
                if confirm is False:
                    yield FormattedText([("class:warning", "Canceled!")])
                    return
                if confirm is True:
                    yield FormattedText([("class:warning", "Your Call!!")])

            self.pre_hook(raw_command, command_name, args, completer)
            # if raw_command is not supposed to send to server
            if input_command_upper in CLIENT_COMMANDS:
                logger.info(f"{input_command_upper} is an iredis command.")
                yield from self.client_execute_command(command_name, *args)
                return

            redis_resp = self.execute(command_name, *args)
            # if shell, do not render, just run in shell pipe and show the
            # subcommand's stdout/stderr
            if shell_command:
                # pass the raw response of redis to shell command
                if isinstance(redis_resp, list):
                    stdin = b"\n".join(redis_resp)
                else:
                    stdin = redis_resp
                run(shell_command, input=stdin, stdout=sys.stdout, shell=True)
                return

            self.after_hook(raw_command, command_name, args, completer, redis_resp)
            yield self.render_response(redis_resp, command_name)

            # FIXME generator response do not support pipeline
            if input_command_upper == "MONITOR":
                # TODO special render for monitor
                try:
                    yield from self.monitor()
                except KeyboardInterrupt:
                    pass
            elif input_command_upper in [
                "SUBSCRIBE",
                "PSUBSCRIBE",
            ]:  # enter subscribe mode
                try:
                    yield from self.subscribing()
                except KeyboardInterrupt:
                    yield from self.unsubscribing()
        except Exception as e:
            logger.exception(e)
            yield OutputRender.render_error(str(e))
        finally:
            config.withscores = False

    def after_hook(self, command, command_name, args, completer, response):
        # === After hook ===
        # SELECT db on AUTH
        if command_name.upper() == "AUTH":
            if self.db:
                select_result = self.execute("SELECT", self.db)
                if nativestr(select_result) != "OK":
                    raise ConnectionError("Invalid Database")
            # When the connection is TimeoutError or ConnectionError, reconnect the connection will use it
            self.connection.password = args[0]
        elif command_name.upper() == "SELECT":
            logger.debug("[After hook] Command is SELECT, change self.db.")
            self.db = int(args[0])
            # When the connection is TimeoutError or ConnectionError, reconnect the connection will use it
            self.connection.db = self.db
        elif command_name.upper() == "MULTI":
            logger.debug("[After hook] Command is MULTI, start transaction.")
            config.transaction = True

        if completer:
            completer.update_completer_for_response(command_name, response)

    def pre_hook(self, command, command_name, args, completer: IRedisCompleter):
        """
        Before execute command, patch completers first.
        Eg: When user run `GET foo`, key completer need to
          touch foo.

        Only works when compile-grammar thread is done.
        """
        # TRANSATION state chage
        if command_name.upper() in ["EXEC", "DISCARD"]:
            logger.debug(f"[After hook] Command is {command_name}, unset transaction.")
            config.transaction = False
        # score display for sorted set
        if command_name.upper() in ["ZSCAN", "ZPOPMAX", "ZPOPMIN"]:
            config.withscores = True

        # not a tty
        if not completer:
            logger.warning(
                "[Pre patch completer] Complter is None, not a tty, "
                "not patch completers, not set withscores"
            )
            return
        completer.update_completer_for_input(command)

        redis_grammar = completer.get_completer(command).compiled_grammar
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

    def do_help(self, *args):
        command_docs_name = "-".join(args).lower()
        command_summary_name = " ".join(args).upper()
        try:
            doc = read_text(commands_data, f"{command_docs_name}.md")
        except FileNotFoundError:
            raise NotRedisCommand(
                f"{command_summary_name} is not a valide Redis command."
            )
        rendered_detail = markdown.render(doc)
        summary_dict = commands_summary[command_summary_name]

        avaiable_version = summary_dict.get("since", "?")
        server_version = config.version
        # FIXME anything strange with single quotes?
        logger.debug(f"[--version--] '{server_version}'")
        try:
            is_avaiable = StrictVersion(server_version) > StrictVersion(
                avaiable_version
            )
        except Exception as e:
            logger.exception(e)
            is_avaiable = None

        if is_avaiable:
            avaiable_text = f"(Avaiable on your redis-server: {server_version})"
        elif is_avaiable is False:
            avaiable_text = f"(Not avaiable on your redis-server: {server_version})"
        else:
            avaiable_text = ""
        since_text = f"{avaiable_version} {avaiable_text}"

        summary = [
            ("", "\n"),
            ("class:doccommand", "  " + command_summary_name),
            ("", "\n"),
            ("class:dockey", "  summary: "),
            ("", summary_dict.get("summary", "No summary")),
            ("", "\n"),
            ("class:dockey", "  complexity: "),
            ("", summary_dict.get("complexity", "?")),
            ("", "\n"),
            ("class:dockey", "  since: "),
            ("", since_text),
            ("", "\n"),
            ("class:dockey", "  group: "),
            ("", summary_dict.get("group", "?")),
            ("", "\n"),
            ("class:dockey", "  syntax: "),
            ("", command_summary_name),  # command
            *compose_command_syntax(summary_dict, style_class=""),  # command args
            ("", "\n\n"),
        ]

        return FormattedText(summary + rendered_detail)

    def do_peek(self, key):
        """
        PEEK command implementation.

        It's a generator, will run different redis commands based on the key's
        type, yields FormattedText once a command reached result.

        Redis current supported types:
            string, list, set, zset, hash and stream.
        """

        def _string(key):
            strlen = self.execute("strlen", key)
            yield FormattedText([("class:dockey", "strlen: "), ("", str(strlen))])

            value = self.execute("GET", key)
            yield FormattedText(
                [
                    ("class:dockey", "value: "),
                    ("", renders.OutputRender.render_bulk_string(value)),
                ]
            )

        def _list(key):
            llen = self.execute("llen", key)
            yield FormattedText([("class:dockey", "llen: "), ("", str(llen))])
            if llen <= 20:
                contents = self.execute(f"LRANGE {key} 0 -1")
            else:
                first_10 = self.execute(f"LRANGE {key} 0 9")
                last_10 = self.execute(f"LRANGE {key} -10 -1")
                contents = first_10 + [f"{llen-20} elements was omitted ..."] + last_10
            yield FormattedText([("class:dockey", "elements: ")])
            yield renders.OutputRender.render_list(contents)

        def _set(key):
            cardinality = self.execute("scard", key)
            yield FormattedText(
                [("class:dockey", "cardinality: "), ("", str(cardinality))]
            )
            if cardinality <= 20:
                contents = self.execute("smembers", key)
                yield FormattedText([("class:dockey", "members: ")])
                yield renders.OutputRender.render_list(contents)
            else:
                _, contents = self.execute(f"sscan {key} 0 count 20")
                first_n = len(contents)
                yield FormattedText([("class:dockey", f"members (first {first_n}): ")])
                yield renders.OutputRender.render_members(contents)
                # TODO update completers

        def _zset(key):
            count = self.execute(f"zcount {key} -inf +inf")
            yield FormattedText([("class:dockey", "zcount: "), ("", str(count))])
            if count <= 20:
                contents = self.execute(f"zrange {key} 0 -1 withscores")
                yield FormattedText([("class:dockey", "members: ")])
                yield renders.OutputRender.render_members(contents)
            else:
                _, contents = self.execute(f"zscan {key} 0 count 20")
                first_n = len(contents) // 2
                yield FormattedText([("class:dockey", f"members (first {first_n}): ")])
                config.withscores = True
                output = renders.OutputRender.render_members(contents)
                config.withscores = False
                yield output

        def _hash(key):
            hlen = self.execute(f"hlen {key}")
            yield FormattedText([("class:dockey", "hlen: "), ("", str(hlen))])
            if hlen <= 20:
                contents = self.execute(f"hgetall {key}")
                yield FormattedText([("class:dockey", "fields: ")])
            else:
                _, contents = self.execute(f"hscan {key} 0 count 20")
                first_n = len(contents) // 2
                yield FormattedText([("class:dockey", f"fields (first {first_n}): ")])
            yield renders.OutputRender.render_hash_pairs(contents)

        def _stream(key):
            xinfo = self.execute("xinfo stream", key)
            yield FormattedText([("class:dockey", "XINFO: ")])
            yield renders.OutputRender.render_list(xinfo)

        def _none(key):
            yield f"Key {key} doesn't exist."

        resp = nativestr(self.execute("type", key))
        # FIXME raw write_result parse FormattedText
        yield FormattedText([("class:dockey", "type: "), ("", resp)])

        if resp == "none":
            return

        encoding = nativestr(self.execute("object encoding", key))
        yield FormattedText([("class:dockey", "object encoding: "), ("", encoding)])

        memory_usage = str(self.execute("memory usage", key))
        yield FormattedText(
            [("class:dockey", "memory usage(bytes): "), ("", memory_usage)]
        )

        ttl = str(self.execute("ttl", key))
        yield FormattedText([("class:dockey", "ttl: "), ("", ttl)])

        yield from {
            "string": _string,
            "list": _list,
            "set": _set,
            "zset": _zset,
            "hash": _hash,
            "stream": _stream,
            "none": _none,
        }[resp](key)
