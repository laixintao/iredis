# -*- coding: utf-8 -*-
import os
import logging
import sys
import time
from pathlib import Path
import platform

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding.bindings.named_commands import (
    register as prompt_register,
)

from .client import Client
from .key_bindings import kb as key_bindings
from .style import STYLE
from .config import config, load_config_files
from .processors import UserInputCommand, UpdateBottomProcessor, PasswordProcessor
from .bottom import BottomToolbar
from .utils import timer, exit, convert_formatted_text_to_bytes, parse_url
from .completers import IRedisCompleter
from .lexer import IRedisLexer
from . import __version__

logger = logging.getLogger(__name__)


class SkipAuthFileHistory(FileHistory):
    """Exactlly like FileHistory, but won't save `AUTH` command into history
    file."""

    def append_string(self, string: str) -> None:
        if string.lstrip().upper().startswith("AUTH"):
            return
        super().append_string(string)


def setup_log():
    if config.log_location:
        logging.basicConfig(
            filename=os.path.expanduser(config.log_location),
            filemode="a",
            format="%(levelname)5s %(message)s",
            level="DEBUG",
        )
    else:
        logging.disable(logging.CRITICAL)
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


def is_too_tall(text, max_height):
    if isinstance(text, FormattedText):
        text = convert_formatted_text_to_bytes(text)
    lines = len(text.split(b"\n"))
    return lines > max_height


def write_result(text, max_height=None):
    """
    When config.raw set to True, write text(must be bytes in that case)
    directly to stdout, same if text is bytes.

    :param text: is_raw: bytes or str, not raw: FormattedText
    :is_raw: bool
    """
    logger.info(f"Print result {type(text)}: {text}"[:200])

    # this function only handle bytes or FormattedText
    # if it's str, convert to bytes
    if isinstance(text, str):
        if config.decode:
            text = text.encode(config.decode)
        else:
            text = text.encode()

    # using pager if too tall
    if max_height and config.enable_pager and is_too_tall(text, max_height):
        if isinstance(text, FormattedText):
            text = convert_formatted_text_to_bytes(text)
            os.environ["LESS"] = "-SRX"
        # click.echo_via_pager only accepts str
        if config.decode:
            text = text.decode(config.decode)
        else:
            text = text.decode()
        # TODO current pager doesn't support colors
        click.echo_via_pager(text)
        return

    if isinstance(text, bytes):
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
                input_processors=[
                    UpdateBottomProcessor(command_holder, session),
                    PasswordProcessor(),
                ],
                rprompt=lambda: "<transaction>" if config.transaction else None,
                key_bindings=key_bindings,
                enable_suspend=True,
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
                write_result(
                    answer,
                    # -1 is because 127.0.0.1:6379> takes one line
                    session.output.get_size().rows - session.reserve_space_for_menu - 1,
                )
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
DECODE_HELP = """
decode response, default is No decode, which will output all bytes literals.
"""
RAINBOW = "Display colorful prompt."
DSN_HELP = """
Use DSN configured into the [alias_dsn] section of iredisrc file. \
(Can set with env `IREDIS_DSN`)
"""
URL_HELP = """
Use Redis URL to indicate connection(Can set with env `IREDIS_URL`), Example:
    redis://[[username]:[password]]@localhost:6379/0
    rediss://[[username]:[password]]@localhost:6379/0
    unix://[[username]:[password]]@/path/to/socket.sock?db=0
"""
SHELL = """Allow to run shell commands, default to True."""
PAGER_HELP = """Using pager when output is too tall for your window, default to True."""


# command line entry here...
@click.command()
@click.pass_context
@click.option("-h", help="Server hostname (default: 127.0.0.1).", default="127.0.0.1")
@click.option("-p", help="Server port (default: 6379).", default="6379")
@click.option(
    "-s", "--socket", default=None, help="Server socket (overrides hostname and port)."
)
@click.option(
    "-n", help="Database number.(overwrites dsn/url's db number)", default=None
)
@click.option("-a", "--password", help="Password to use when connecting to the server.")
@click.option("--url", default=None, envvar="IREDIS_URL", help=URL_HELP)
@click.option("-d", "--dsn", default=None, envvar="IREDIS_DSN", help=DSN_HELP)
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
@click.option("--client_name", help="Assign a name to the current connection.")
@click.option("--raw/--no-raw", default=None, is_flag=True, help=RAW_HELP)
@click.option("--rainbow/--no-rainbow", default=None, is_flag=True, help=RAINBOW)
@click.option("--shell/--no-shell", default=None, is_flag=True, help=SHELL)
@click.option("--pager/--no-pager", default=None, is_flag=True, help=PAGER_HELP)
@click.version_option()
@click.argument("cmd", nargs=-1)
def gather_args(
    ctx,
    h,
    p,
    n,
    password,
    client_name,
    newbie,
    iredisrc,
    decode,
    raw,
    rainbow,
    cmd,
    dsn,
    url,
    socket,
    shell,
    pager,
):
    """
    IRedis: Interactive Redis

    When no command is given, IRedis starts in interactive mode.

    \b
    Examples:
      - iredis
      - iredis -d dsn
      - iredis -h 127.0.0.1 -p 6379
      - iredis -h 127.0.0.1 -p 6379 -a <password>
      - iredis --url redis://localhost:7890/3

    Type "help" in interactive mode for information on available commands
    and settings.
    """
    load_config_files(iredisrc)
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
    if shell is not None:
        config.shell = shell
    if pager is not None:
        config.enable_pager = pager

    return ctx


@prompt_register("edit-and-execute-command")
def edit_and_execute(event):
    """Different from the prompt-toolkit default, we want to have a choice not
    to execute a query after editing, hence validate_and_handle=False."""
    buff = event.current_buffer
    # this will prevent running command immediately when exit editor.
    buff.open_in_editor(validate_and_handle=False)


def resolve_dsn(dsn):
    try:
        dsn_uri = config.alias_dsn[dsn]
    except KeyError:
        click.secho(
            "Could not find the specified DSN in the config file. "
            'Please check the "[alias_dsn]" section in your '
            "iredisrc.",
            err=True,
            fg="red",
        )
        sys.exit(1)
    return dsn_uri


def create_client(params):
    """
    Create a Client.
    :param params: commandline params.
    """
    host = params["h"]
    port = params["p"]
    db = params["n"]
    password = params["password"]
    client_name = params["client_name"]

    dsn_from_url = None
    dsn = params["dsn"]
    if config.alias_dsn and dsn:
        dsn_uri = resolve_dsn(dsn)
        dsn_from_url = parse_url(dsn_uri)
    if params["url"]:
        dsn_from_url = parse_url(params["url"])
    if dsn_from_url:
        # db from command lint options should be high priority
        db = db if db else dsn_from_url.db
        return Client(
            host=dsn_from_url.host,
            port=dsn_from_url.port,
            db=db,
            password=dsn_from_url.password,
            path=dsn_from_url.path,
            scheme=dsn_from_url.scheme,
            username=dsn_from_url.username,
            client_name=client_name,
        )
    if params["socket"]:
        return Client(
            scheme="unix",
            path=params["socket"],
            db=db,
            password=password,
            client_name=client_name,
        )
    return Client(
        host=host, port=port, db=db, password=password, client_name=client_name
    )


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

    # redis client
    client = create_client(ctx.params)

    if not sys.stdin.isatty():
        for line in sys.stdin.readlines():
            logger.debug(f"[Command stdin] {line}")
            for answer in client.send_command(line, None):
                write_result(answer)
        return

    # no interactive mode, directly run a command
    if ctx.params["cmd"]:
        answers = client.send_command(" ".join(ctx.params["cmd"]), None)
        for answer in answers:
            write_result(answer)
        logger.warning("[OVER] command executed, exit...")
        return

    # prompt session
    session = PromptSession(
        history=SkipAuthFileHistory(Path(os.path.expanduser(config.history_location))),
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
