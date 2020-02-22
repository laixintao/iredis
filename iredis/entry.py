# -*- coding: utf-8 -*-
import os
import logging
import warnings
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import platform

import click

from redis.connection import Connection, SSLConnection, UnixDomainSocketConnection
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text
from prompt_toolkit.key_binding.bindings.named_commands import (
    register as prompt_register,
)

from .client import Client
from .style import STYLE
from .config import config, load_config_files
from .processors import UserInputCommand, GetCommandProcessor
from .bottom import BottomToolbar
from .utils import timer, exit
from .completers import IRedisCompleter
from .lexer import IRedisLexer
from . import __version__


logger = logging.getLogger(__name__)
HISTORY_FILE = Path(os.path.expanduser("~")) / ".iredis_history"


def setup_log():
    if config.log_location:
        logging.basicConfig(
            filename=os.path.expanduser(config.log_location),
            filemode="a",
            format="%(levelname)5s %(message)s",
            level="DEBUG",
        )
    logger.info("------ iRedis ------")


def greetings():
    iredis_version = f"iredis  {__version__} (Python {platform.python_version()})"
    if config.no_version_reason:
        reason = f"({config.no_version_reason})"
    else:
        reason = ""

    server_version = f"redis-server  {config.version} {reason}"
    home_page = "Home:   https://iredis.io"
    issues = "Issues: https://iredis.io/issues"
    display = "\n".join([iredis_version, server_version, home_page, issues])
    if config.raw:
        display = display.encode()
    write_result(display)


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


def write_result(text):
    """
    :param text: is_raw: bytes or str, not raw: FormattedText
    :is_raw: bool
    """
    logger.info(f"write: {text}")
    if config.raw:
        if isinstance(text, str):
            text = text.encode(config.decode)
        sys.stdout.buffer.write(text)
        sys.stdout.write("\n")
    else:
        print_formatted_text(text, end="", style=STYLE)
        print_formatted_text()


class Rainbow:
    color = [
        ("#cc2244"),
        ("#bb4444"),
        ("#996644"),
        ("#cc8844"),
        ("#ccaa44"),
        ("#bbaa44"),
        ("#99aa44"),
        ("#778844"),
        ("#55aa44"),
        ("#33aa44"),
        ("#11aa44"),
        ("#11aa66"),
        ("#11aa88"),
        ("#11aaaa"),
        ("#11aacc"),
        ("#11aaee"),
    ]

    def __init__(self):
        self.current = -1
        self.forword = 1

    def __iter__(self):
        return self

    def __next__(self):
        self.current += self.forword
        if 0 <= self.current < len(self.color):
            # not to the end
            return self.color[self.current]
        else:
            self.forword = -self.forword
            self.current += 2 * self.forword
            return self.color[self.current]


def prompt_message(client):
    # TODO custome prompt
    text = "{hostname}> ".format(hostname=str(client))
    if config.rainbow:
        return list(zip(Rainbow(), text))
    return text


def repl(client, session, start_time):
    command_holder = UserInputCommand()
    timer(f"First REPL command enter, time cost: {time.time() - start_time}")

    while True:
        logger.info("↓↓↓↓" * 10)
        logger.info("REPL waiting for command...")

        try:
            command = session.prompt(
                prompt_message(client),
                bottom_toolbar=BottomToolbar(command_holder).render
                if config.bottom_bar
                else None,
                input_processors=[GetCommandProcessor(command_holder, session)],
                rprompt=lambda: "<transaction>" if config.transaction else None,
            )

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt!")
            continue
        except EOFError:
            exit()
        command = command.strip()
        logger.info(f"[Command] {command}")

        # blank input
        if not command:
            continue

        try:
            answers = client.send_command(command, session.completer)
            for answer in answers:
                write_result(answer)
        # Error with previous command or exception
        except Exception as e:
            logger.exception(e)
            # TODO red error color
            print("(error)", str(e))


RAW_HELP = """
Use raw formatting for replies (default when STDOUT is not a tty). \
However, you can use --no-raw to force formatted output even \
when STDOUT is not a tty.
"""
DECODE_HELP = (
    "decode response, defult is No decode, which will output all bytes literals."
)
RAINBOW = "Display colorful prompt."


# command line entry here...
@click.command()
@click.pass_context
@click.option("-h", help="Server hostname (default: 127.0.0.1).", default="127.0.0.1")
@click.option("-p", help="Server port (default: 6379).", default="6379")
@click.option("-n", help="Database number.", default=None)
@click.option("-a", "--password", help="Password to use when connecting to the server.")
@click.option(
    "-d",
    "--dsn",
    default="",
    envvar="DSN",
    help="Use DSN configured into the [alias_dsn] section of iredisrc file.",
)
@click.option(
    "--newbie/--no-newbie",
    default=None,
    is_flag=True,
    help="Show command hints and useful helps.",
)
@click.option(
    "--iredisrc",
    default="~/.iredisrc",
    help="Config file for iredis, default is ~/.iredisrc.",
)
@click.option("--decode", default=None, help=DECODE_HELP)
@click.option("--raw/--no-raw", default=None, is_flag=True, help=RAW_HELP)
@click.option("--rainbow/--no-rainbow", default=None, is_flag=True, help=RAINBOW)
@click.version_option()
@click.argument("cmd", nargs=-1)
def gather_args(
    ctx, h, p, n, password, newbie, iredisrc, decode, raw, rainbow, cmd, dsn
):
    """
    IRedis: Interactive Redis

    When no command is given, redis-cli starts in interactive mode.

    \b
    Examples:
      - iredis
      - iredis -d dsn
      - iredis -h 127.0.0.1 -p 6379
      - iredis -h 127.0.0.1 -p 6379 -a <password>

    Type "help" in interactive mode for information on available commands
    and settings.
    """
    config_obj = load_config_files(iredisrc)
    setup_log()
    logger.info(
        f"[commandline args] host={h}, port={p}, db={n}, newbie={newbie}, "
        f"iredisrc={iredisrc}, decode={decode}, raw={raw}, "
        f"cmd={cmd}, rainbow={rainbow}."
    )
    # raw config
    if raw is not None:
        config.raw = raw
    if not sys.stdout.isatty():
        config.raw = True

    config.newbie_mode = newbie

    if decode is not None:
        config.decode = decode
    if rainbow is not None:
        config.rainbow = rainbow

    # gather connection_kwargs
    config.connection_class = Connection
    config.connection_kwargs = {}
    config.connection_kwargs["host"] = h or config.hostname
    config.connection_kwargs["port"] = p or config.port
    config.connection_kwargs["password"] = password or config.password
    config.connection_kwargs["socket_keepalive"] = config.socket_keepalive

    if config.decode:
        config.connection_kwargs["encoding"] = config.decode
        config.connection_kwargs["decode_responses"] = True
        config.connection_kwargs["encoding_errors"] = "replace"
    else:
        config.connection_kwargs["decode_responses"] = False

    dsn_uri = None
    if config_obj["alias_dsn"] and dsn:
        try:
            dsn_uri = config_obj["alias_dsn"].get(dsn)
        except KeyError:
            click.secho(
                "Could not find the specified DSN in the config file. "
                'Please check the "[alias_dsn]" section in your '
                "iredisrc.",
                err=True,
                fg="red",
            )
            exit(1)

    if dsn_uri:
        parse_url(dsn_uri)

    return ctx


<<<<<<< HEAD
@prompt_register("edit-and-execute-command")
def edit_and_execute(event):
    """Different from the prompt-toolkit default, we want to have a choice not
    to execute a query after editing, hence validate_and_handle=False."""
    buff = event.current_buffer
    # this will prevent running command immediately when exit editor.
    buff.open_in_editor(validate_and_handle=False)
=======
FALSE_STRINGS = ("0", "F", "FALSE", "N", "NO")


def to_bool(value):
    if value is None or value == "":
        return None
    if isinstance(value, str) and value.upper() in FALSE_STRINGS:
        return False
    return bool(value)


URL_QUERY_ARGUMENT_PARSERS = {
    "socket_timeout": float,
    "socket_connect_timeout": float,
    "socket_keepalive": to_bool,
    "retry_on_timeout": to_bool,
    "max_connections": int,
    "health_check_interval": int,
    "ssl_check_hostname": to_bool,
}


def parse_url(url):
    """
    Update config.connection_kwargs and config.connection_class from the given URL.

    For example::

        redis://[[username]:[password]]@localhost:6379/0
        rediss://[[username]:[password]]@localhost:6379/0
        unix://[[username]:[password]]@/path/to/socket.sock?db=0

    Three URL schemes are supported:

    - ```redis://``
        <https://www.iana.org/assignments/uri-schemes/prov/redis>`_ creates a
        normal TCP socket connection
    - ```rediss://``
        <https://www.iana.org/assignments/uri-schemes/prov/rediss>`_ creates
        a SSL wrapped TCP socket connection
    - ``unix://`` creates a Unix Domain Socket connection

    There are several ways to specify a database number. The parse function
    will return the first specified option:
        1. A ``db`` querystring option, e.g. redis://localhost?db=0
        2. If using the redis:// scheme, the path argument of the url, e.g.
            redis://localhost/0
        3. The ``db`` argument to this function.

    If none of these options are specified, db=0 is used.

    The ``decode_components`` argument allows this function to work with
    percent-encoded URLs. If this argument is set to ``True`` all ``%xx``
    escapes will be replaced by their single-character equivalents after
    the URL has been parsed. This only applies to the ``hostname``,
    ``path``, ``username`` and ``password`` components.

    Any additional querystring arguments and keyword arguments will be
    passed along to the ConnectionPool class's initializer. The querystring
    arguments ``socket_connect_timeout`` and ``socket_timeout`` if supplied
    are parsed as float values. The arguments ``socket_keepalive`` and
    ``retry_on_timeout`` are parsed to boolean values that accept
    True/False, Yes/No values to indicate state. Invalid types cause a
    ``UserWarning`` to be raised. In the case of conflicting arguments,
    querystring arguments always win.

    """
    url = urlparse(url)
    url_options = {}

    for name, value in parse_qs(url.query):
        if value and len(value) > 0:
            parser = URL_QUERY_ARGUMENT_PARSERS.get(name)
            if parser:
                try:
                    url_options[name] = parser(value[0])
                except (TypeError, ValueError):
                    warnings.warn(
                        UserWarning("Invalid value for `%s` in connection URL." % name)
                    )
            else:
                url_options[name] = value[0]

    username = unquote(url.username) if url.username else None
    password = unquote(url.password) if url.password else None
    path = unquote(url.path) if url.path else None
    hostname = unquote(url.hostname) if url.hostname else None

    # We only support redis://, rediss:// and unix:// schemes.
    if url.scheme == "unix":
        config.connection_class = UnixDomainSocketConnection
        config.connection_kwargs.pop("host", None)
        config.connection_kwargs.pop("port", None)
        config.connection_kwargs.pop("socket_keepalive", None)
        url_options.update({"username": username, "password": password, "path": path})

    elif url.scheme in ("redis", "rediss"):
        url_options.update(
            {
                "host": hostname,
                "port": int(url.port or 6379),
                "username": username,
                "password": password,
            }
        )

        # If there's a path argument, use it as the db argument if a
        # querystring value wasn't specified
        if "db" not in url_options and path:
            try:
                url_options["db"] = int(path.replace("/", ""))
            except (AttributeError, ValueError):
                pass

        if url.scheme == "rediss":
            config.connection_class = SSLConnection
    else:
        valid_schemes = ", ".join(("redis://", "rediss://", "unix://"))
        raise ValueError(
            "Redis URL must specify one of the following" "schemes (%s)" % valid_schemes
        )

    # last shot at the db value
    url_options["db"] = int(url_options.get("db", 0))

    # update the arguments from the URL values
    for k, v in url_options.items():
        if k not in config.connection_kwargs:
            config.connection_kwargs[k] = v
>>>>>>> support dsn with connection_kwargs and connection_class


def main():
    enter_main_time = time.time()  # just for logs

    # invoke in non-standalone mode to gather args
    ctx = None
    try:
        ctx = gather_args.main(standalone_mode=False)
    except click.exceptions.NoSuchOption as nosuchoption:
        nosuchoption.show()
    except click.exceptions.BadOptionUsage as badoption:
        if badoption.option_name == "-h":
            # -h without host, is short command for --help
            # like redis-cli
            print_help_msg(gather_args)
        return
    if not ctx:  # called help
        return
    # TODO merge config file and commandline options here
    # ctx.params > pwd config > user conifg > system config > default
    # ignore None value

    # redis client
    client = Client(
        ctx.params["h"], ctx.params["p"], ctx.params["n"], ctx.params["password"]
    )

    if not sys.stdin.isatty():
        for line in sys.stdin.readlines():
            logger.debug(f"[Command stdin] {line}")
            for answer in client.send_command(line, None):
                write_result(answer)
        return

    if ctx.params["cmd"]:  # no interactive mode
        answers = client.send_command(" ".join(ctx.params["cmd"]), None)
        for answer in answers:
            write_result(answer)
        logger.warning("[OVER] command executed, exit...")
        return

    # Create history file if not exists.
    if not os.path.exists(HISTORY_FILE):
        logger.info(f"History file {HISTORY_FILE} not exists, create now...")
        f = open(HISTORY_FILE, "w+")
        f.close()

    # prompt session
    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        style=STYLE,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True,
        lexer=IRedisLexer(),
        completer=IRedisCompleter(
            hint=config.newbie_mode, completion_casing=config.completion_casing
        ),
        enable_open_in_editor=True,
        tempfile_suffix=".redis",
    )

    # print hello message
    greetings()
    repl(client, session, enter_main_time)
