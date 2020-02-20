# -*- coding: utf-8 -*-
import os
import logging
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse
import platform

import click
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

    dsn_uri = None

    if config_obj["alias_dsn"] and dsn:
        try:
            dsn_uri = config_obj["alias_dsn"][dsn]
        except KeyError:
            click.secho(
                "Could not find the specified DSN in the config file. "
                'Please check the "[alias_dsn]" section in your '
                "iredisrc.",
                err=True,
                fg="red",
            )
            exit(1)
    config.dsn_uri = dsn_uri
    return ctx


@prompt_register("edit-and-execute-command")
def edit_and_execute(event):
    """Different from the prompt-toolkit default, we want to have a choice not
    to execute a query after editing, hence validate_and_handle=False."""
    buff = event.current_buffer
    # this will prevent running command immediately when exit editor.
    buff.open_in_editor(validate_and_handle=False)


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
    if config.dsn_uri:
        client = Client.from_url(config.dsn_uri)
    else:
        client = Client(
            ctx.params["h"], ctx.params["p"], ctx.params["n"], ctx.params["password"],
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
