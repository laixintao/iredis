"""
IRedis client.
"""
import re
import logging
import sys
from distutils.version import StrictVersion
from subprocess import Popen, PIPE

import redis
from redis.connection import Connection
from redis.exceptions import TimeoutError, ConnectionError, AuthenticationError
from prompt_toolkit.formatted_text import FormattedText

from . import renders
from . import markdown
from . import utils, project_data
from .config import config
from .commands_csv_loader import all_commands, command2callback, commands_summary
from .utils import nativestr, split_command_args, _strip_quote_args
from .utils import compose_command_syntax
from .renders import render_error, render_bulk_string_decode, render_subscribe
from .completers import LatestUsedFirstWordCompleter
from .exceptions import NotRedisCommand

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
        self.callbacks = self.reder_funcname_mapping()
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
        self.connection.send_command("INFO")
        # safe to decode Redis's INFO response
        info_resp = utils.ensure_str(self.connection.read_response())

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
            return self.do_help(*args)

    def execute_command_and_read_response(
        self, completer, command_name, *args, **options
    ):
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

    def _dynamic_render(self, command_name, response, completer):
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
        # not implemented command, use no conversion
        # this `else` should be deleted finally
        else:
            rendered = response
        logger.info(f"[rendered] {rendered}")
        return rendered

    def render_response(self, response, completer, command_name):
        "Parses a response from the Redis server"
        logger.info(f"[Redis-Server] Response: {response}")
        # if in transaction, use queue render first
        if config.transaction:
            callback = renders.render_transaction_queue
            rendered = callback(response, completer)
        else:
            rendered = self._dynamic_render(command_name, response, completer)
        return rendered

    def monitor(self):
        """Redis' MONITOR command:
        https://redis.io/commands/monitor
        This command need to read from a stream resp, so
        it's different
        """
        while 1:
            response = self.connection.read_response()
            yield render_bulk_string_decode(response)

    def subscribing(self):
        while 1:
            response = self.connection.read_response()
            yield render_subscribe(response)

    def unsubscribing(self):
        "unsubscribe from all channels"
        self.connection.send_command("UNSUBSCRIBE")
        response = self.connection.read_response()
        yield render_subscribe(response)

    def split_command_and_pipeline(self, rawinput, grammar):
        """
        split user raw input to redis command and shell pipeline.
        eg:
        GET json | jq .key
        return: GET json, jq . key
        """
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

    def send_command(self, raw_command, completer=None):
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
                raw_command, completer.compiled_grammar
            )
        logger.info(f"[Prepare command] Redis: {redis_command}, Shell: {shell_command}")
        try:
            command_name = ""
            command_name, args = split_command_args(redis_command, all_commands)
            # if raw_command is not supposed to send to server
            if command_name.upper() in CLIENT_COMMANDS:
                redis_resp = self.client_execute_command(command_name, *args)
                yield redis_resp
                return
            self.pre_hook(raw_command, command_name, args, completer)
            redis_resp = self.execute_command_and_read_response(
                completer, command_name, *args
            )
            # if shell, do not render, just run in shell pipe and show the
            # subcommand's stdout/stderr
            if shell_command:
                # pass the raw response of redis to shell command
                if isinstance(redis_resp, list):
                    stdin = b"\n".join(redis_resp)
                else:
                    stdin = redis_resp
                shell_resp = Popen(
                    shell_command, stdout=sys.stdout, stdin=PIPE, shell=True
                )
                shell_resp.communicate(stdin)

                return

            self.after_hook(raw_command, command_name, args, completer)
            yield self.render_response(redis_resp, completer, command_name)

            # FIXME generator response do not support pipeline
            if command_name.upper() == "MONITOR":
                # TODO special render for monitor
                try:
                    yield from self.monitor()
                except KeyboardInterrupt:
                    pass
            elif command_name.upper() in [
                "SUBSCRIBE",
                "PSUBSCRIBE",
            ]:  # enter subscribe mode
                try:
                    yield from self.subscribing()
                except KeyboardInterrupt:
                    yield from self.unsubscribing()
        except Exception as e:
            logger.exception(e)
            yield render_error(str(e))
        finally:
            config.withscores = False

    def after_hook(self, command, command_name, args, completer):
        # === After hook ===
        # SELECT db on AUTH
        if command_name.upper() == "AUTH":
            if self.db:
                select_result = self.execute_command_and_read_response(
                    completer, "SELECT", self.db
                )
                if nativestr(select_result) != "OK":
                    raise ConnectionError("Invalid Database")
            # When the connection is TimeoutError or ConnectionError, reconnect the connection will use it
            self.connection.password = args[0]
        elif command_name.upper() == "SELECT":
            logger.debug("[After hook] Command is SELECT, change self.db.")
            self.db = int(args[0])
            # When the connection is TimeoutError or ConnectionError, reconnect the connection will use it
            self.connection.db = self.db
        if command_name.upper() == "MULTI":
            logger.debug("[After hook] Command is MULTI, start transaction.")
            config.transaction = True

    def pre_hook(self, command, command_name, args, completer):
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

        # patch completers
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

    def do_help(self, *args):
        command_docs_name = "-".join(args).lower()
        command_summary_name = " ".join(args).upper()
        try:
            doc_file = open(project_data / "commands" / f"{command_docs_name}.md")
        except FileNotFoundError:
            raise NotRedisCommand(
                f"{command_summary_name} is not a valide Redis command."
            )

        with doc_file as doc_file:
            doc = doc_file.read()
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
