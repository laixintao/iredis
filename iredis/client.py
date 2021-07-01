"""
IRedis client.
"""
import re
import os
import sys
import logging
from subprocess import run
from importlib_resources import read_text
from distutils.version import StrictVersion

import redis
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.formatted_text import FormattedText
from redis.connection import Connection, SSLConnection, UnixDomainSocketConnection
from redis.exceptions import (
    AuthenticationError,
    ConnectionError,
    TimeoutError,
    ResponseError,
)


from . import markdown, renders
from .data import commands as commands_data
from .commands import (
    command2callback,
    commands_summary,
    command2syntax,
    groups,
    split_command_args,
    split_unknown_args,
)
from .completers import IRedisCompleter
from .config import config
from .exceptions import NotRedisCommand, InvalidArguments, AmbiguousCommand, NotSupport
from .renders import OutputRender
from .utils import (
    compose_command_syntax,
    nativestr,
    exit,
    convert_formatted_text_to_bytes,
    parse_url,
)
from .warning import confirm_dangerous_command

logger = logging.getLogger(__name__)
CLIENT_COMMANDS = groups["iredis"]


class Client:
    """
    iRedis client, hold a redis-py Client to interact with Redis.
    """

    def __init__(
        self,
        host=None,
        port=None,
        db=0,
        password=None,
        path=None,
        scheme="redis",
        username=None,
        client_name=None,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.path = path
        # FIXME username is not using...
        self.username = username
        self.client_name = client_name
        self.scheme = scheme

        self.connection = self.create_connection(
            host,
            port,
            db,
            password,
            path,
            scheme,
            username,
            client_name=client_name,
        )

        # all command upper case
        self.answer_callbacks = command2callback
        self.set_default_pager(config)
        try:
            self.connection.connect()
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        if not config.no_info:
            try:
                self.get_server_info()
            except Exception as e:
                logger.warning(f"[After Connection] {str(e)}")
                config.no_version_reason = str(e)
        else:
            config.no_version_reason = "--no-info flag activated"

        if config.version and re.match(r"([\d\.]+)", config.version):
            self.auth_compat(config.version)

    def create_connection(
        self,
        host=None,
        port=None,
        db=0,
        password=None,
        path=None,
        scheme="redis",
        username=None,
        client_name=None,
    ):
        if scheme in ("redis", "rediss"):
            connection_kwargs = {
                "host": host,
                "port": port,
                "db": db,
                "password": password,
                "socket_keepalive": config.socket_keepalive,
                "client_name": client_name,
            }
            if scheme == "rediss":
                connection_class = SSLConnection
            else:
                connection_class = Connection
        else:
            connection_kwargs = {
                "db": db,
                "password": password,
                "path": path,
                "client_name": client_name,
            }
            connection_class = UnixDomainSocketConnection

        if config.decode:
            connection_kwargs["encoding"] = config.decode
            connection_kwargs["decode_responses"] = True
            connection_kwargs["encoding_errors"] = "replace"

        logger.debug(
            f"connection_class={connection_class}, connection_kwargs={connection_kwargs}"
        )

        return connection_class(**connection_kwargs)

    def auth_compat(self, redis_version: str):
        with_username = StrictVersion(redis_version) >= StrictVersion("6.0.0")
        if with_username:
            command2syntax["AUTH"] = "command_usernamex_password"

    def set_default_pager(self, config):
        configured_pager = config.pager
        os_environ_pager = os.environ.get("PAGER")

        if configured_pager:
            logger.info('Default pager found in config file: "%s"', configured_pager)
            os.environ["PAGER"] = configured_pager
        elif os_environ_pager:
            logger.info(
                'Default pager found in PAGER environment variable: "%s"',
                os_environ_pager,
            )
            os.environ["PAGER"] = os_environ_pager
        else:
            logger.info("No default pager found in environment. Using os default pager")

        # Set default set of less recommended options, if they are not already set.
        # They are ignored if pager is different than less.
        if not os.environ.get("LESS"):
            os.environ["LESS"] = "-SRXF"

    def get_server_info(self):
        # safe to decode Redis's INFO response
        info_resp = nativestr(self.execute("INFO"))
        version = re.findall(r"^redis_version:([\d\.]+)\r\n", info_resp, re.MULTILINE)[
            0
        ]
        logger.debug(f"[Redis Version] {version}")
        config.version = version

    def __str__(self):
        if self.scheme == "unix":
            prompt = f"redis {self.path}"
        else:
            prompt = f"{self.host}:{self.port}"

        if self.db:
            prompt = f"{prompt}[{self.db}]"
        return prompt

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

    def execute(self, *args, **kwargs):
        logger.info(
            f"execute: connection={self.connection} args={args}, kwargs={kwargs}"
        )
        return self.execute_by_connection(self.connection, *args, **kwargs)

    def execute_by_connection(self, connection, command_name, *args, **options):
        """Execute a command and return a parsed response
        Here we retry once for ConnectionError.
        """
        logger.info(
            f"execute by connection: connection={connection}, name={command_name}, {args}, {options}"
        )
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
                    connection.disconnect()
                    connection.connect()
                    logger.info(f"New connection created, retry on {connection}.")
                logger.info(f"send_command: {command_name} , {args}")
                connection.send_command(command_name, *args)
                response = connection.read_response()
            except AuthenticationError:
                raise
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Connection Error, got {e}, retrying...")
                last_error = e
                retry_times -= 1
                need_refresh_connection = True
            except (ResponseError) as e:
                response_message = str(e)
                if response_message.startswith("MOVED"):
                    return self.reissue_with_redirect(
                        response_message, command_name, *args, **options
                    )
                raise e

            except redis.exceptions.ExecAbortError:
                config.transaction = False
                raise
            else:
                return response
        raise last_error

    def reissue_with_redirect(self, response, *args, **kwargs):
        """
        For redis cluster, when server response a "MOVE ..." response, we auto-
        redirect to the target node, reissue the original command.

        This feature is not supported for unix socket connection.
        """
        # Redis Cluster only supports database zero.
        _, slot, ip_port = response.split(" ")
        ip, port = ip_port.split(":")
        port = int(port)

        print(response, file=sys.stderr)

        connection = self.create_connection(ip, port)
        # if user sets dsn for dest node
        # use username and password from dsn settings
        if config.alias_dsn:
            for dsn_name, dsn_url in config.alias_dsn.items():
                dsn = parse_url(dsn_url)
                if dsn.host == ip and dsn.port == port:
                    print(
                        f"Connect {ip}:{port} via dns settings of {dsn_name}",
                        file=sys.stderr,
                    )
                    connection = self.create_connection(
                        dsn.host,
                        dsn.port,
                        dsn.db,
                        dsn.password,
                        dsn.path,
                        dsn.scheme,
                        dsn.username,
                    )
                    break

        connection.connect()
        return self.execute_by_connection(connection, *args, **kwargs)

    def render_response(self, response, command_name):
        "Parses a response from the Redis server"
        logger.info(f"[Redis-Server] Response: {response}")
        if config.raw:
            callback = OutputRender.render_raw
        # if in transaction, use queue render first
        elif config.transaction:
            callback = renders.OutputRender.render_transaction_queue
        else:
            callback = OutputRender.get_render(command_name=command_name)
        rendered = callback(response)
        logger.info(f"[render result] {rendered}")
        return rendered

    def monitor(self):
        """Redis' MONITOR command:
        https://redis.io/commands/monitor
        This command need to read from a stream resp, so
        it's different
        """
        while 1:
            response = self.connection.read_response()
            if config.raw:
                yield OutputRender.render_raw(response)
            else:
                yield OutputRender.render_bulk_string_decode(response)

    def subscribing(self):
        while 1:
            response = self.connection.read_response()
            if config.raw:
                yield OutputRender.render_raw(response)
            else:
                yield OutputRender.render_subscribe(response)

    def unsubscribing(self):
        "unsubscribe from all channels"
        response = self.execute("UNSUBSCRIBE")
        if config.raw:
            yield OutputRender.render_raw(response)
        else:
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
            # invalid command!
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
            try:
                command_name, args = split_command_args(redis_command)
            except (InvalidArguments, AmbiguousCommand):
                logger.warn(
                    "This is not a iredis known command, send to redis-server anyway..."
                )
                command_name, args = split_unknown_args(redis_command)

            logger.info(f"[Split command] command: {command_name}, args: {args}")
            input_command_upper = command_name.upper()
            # Confirm for dangerous command
            if config.warning:
                confirm = confirm_dangerous_command(input_command_upper)
                if confirm is True:
                    print("Your Call!!", file=sys.stderr)
                elif confirm is False:
                    print("Canceled!", file=sys.stderr)
                    return
                # None: continue...

            self.pre_hook(raw_command, command_name, args, completer)
            # if raw_command is not supposed to send to server
            if input_command_upper in CLIENT_COMMANDS:
                logger.info(f"{input_command_upper} is an iredis command.")
                yield from self.client_execute_command(command_name, *args)
                return

            redis_resp = self.execute(command_name, *args)
            # if shell_command and enable shell, do not render, just run in shell pipe and show the
            # subcommand's stdout/stderr
            if shell_command and config.shell:
                # pass the raw response of redis to shell command
                stdin = OutputRender.render_raw(redis_resp)
                run(shell_command, input=stdin, shell=True)
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
            if config.raw:
                render_callback = OutputRender.render_raw
            else:
                render_callback = OutputRender.render_error
            yield render_callback(f"ERROR {str(e)}".encode())
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
            completer.update_completer_for_response(command_name, args, response)

    def pre_hook(self, command, command_name, args, completer: IRedisCompleter):
        """
        Before execute command, patch completers first.
        Eg: When user run `GET foo`, key completer need to
          touch foo.

        Only works when compile-grammar thread is done.
        """
        if command_name.upper() == "HELLO":
            raise NotSupport("IRedis currently not support RESP3, sorry about that.")
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
            # invalid command!
            return
        variables = m.variables()
        # zset withscores
        withscores = variables.get("withscores")
        if withscores:
            config.withscores = True

    def do_help(self, *args):
        command_docs_name = "-".join(args).lower()
        command_summary_name = " ".join(args).upper()
        try:
            doc = read_text(commands_data, f"{command_docs_name}.md")
        except FileNotFoundError:
            raise NotRedisCommand(
                f"{command_summary_name} is not a valid Redis command."
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

        to_render = FormattedText(summary + rendered_detail)
        if config.raw:
            return convert_formatted_text_to_bytes(to_render)
        return to_render

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

        # incase the result is too long, we yield only once so the outputer
        # can pager it.
        peek_response = []
        key_type = nativestr(self.execute("type", key))
        if key_type == "none":
            yield f"{key} doesn't exist."
            return

        encoding = nativestr(self.execute("object encoding", key))

        # use `memory usage` to get memory, this command available from redis4.0
        mem = ""
        if config.version and StrictVersion(config.version) >= StrictVersion("4.0.0"):
            memory_usage_value = str(self.execute("memory usage", key))
            mem = f"  mem: {memory_usage_value} bytes"

        ttl = str(self.execute("ttl", key))

        key_info = f"{key_type} ({encoding}){mem}, ttl: {ttl}"

        # FIXME raw write_result parse FormattedText
        peek_response.append(FormattedText([("class:dockey", "key: "), ("", key_info)]))

        detail_action_fun = {
            "string": _string,
            "list": _list,
            "set": _set,
            "zset": _zset,
            "hash": _hash,
            "stream": _stream,
        }[key_type]
        detail = list(detail_action_fun(key))
        peek_response.extend(detail)

        # merge them into only one FormattedText
        flat_formatted_text_pair = []
        for index, formatted_text in enumerate(peek_response):
            for ft in formatted_text:
                flat_formatted_text_pair.append(ft)
            if index < len(peek_response) - 1:
                flat_formatted_text_pair.append(renders.NEWLINE_TUPLE)

        if config.raw:
            yield convert_formatted_text_to_bytes(flat_formatted_text_pair)
            return
        yield FormattedText(flat_formatted_text_pair)
