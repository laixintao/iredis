# -*- coding: utf-8 -*-
import os
import logging
import sys
import time
from pathlib import Path

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text

from .client import Client
from .style import STYLE
from .config import config, COMPILING_DONE
from .completers import compile_grammar_bg
from .processors import UserInputCommand, GetCommandProcessor
from .bottom import BottomToolbar
from .utils import timer
from . import __version__

logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".iredis_history"


def greetings():
    iredis_version = f"iredis  {__version__}"
    if config.no_version_reason:
        reason = f"({config.no_version_reason})"
    else:
        reason = ""

    server_version = f"redis-server  {config.version} {reason}"
    home_page = "Home:   https://iredis.io"
    issues = "Issues: https://iredis.io/issues"
    display = "\n".join([iredis_version, server_version, home_page, issues])
    write_result(display)


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


def write_result(text):
    """
    :param text: is_raw: bytes, not raw: FormattedText
    :is_raw: bool
    """
    if config.raw:
        sys.stdout.buffer.write(text)
        sys.stdout.write("\n")
    else:
        print_formatted_text(text, end="", style=STYLE)
        print_formatted_text()


def repl(client, session, start_time):
    command_holder = UserInputCommand()
    timer(f"First REPL command enter, time cost: {time.time() - start_time}")

    while True:
        logger.info("↓↓↓↓" * 10)
        logger.info("REPL waiting for command...")
        if config.compiling != COMPILING_DONE:
            # auto refresh to display animation...
            _interval = 0.1
        else:
            _interval = None

        try:
            command = session.prompt(
                "{hostname}> ".format(hostname=str(client)),
                bottom_toolbar=BottomToolbar(command_holder).render,
                refresh_interval=_interval,
                input_processors=[GetCommandProcessor(command_holder)],
                rprompt=lambda: "<transaction>" if config.transaction else None,
            )

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt!")
            continue
        except EOFError:
            print("Goodbye!")
            sys.exit()
        command = command.strip()
        logger.info(f"[Command] {command}")

        # blank input
        if not command:
            continue

        try:
            answer = client.send_command(command, session.completer)
        # Error with previous command or exception
        except Exception as e:
            logger.exception(e)
            # TODO red error color
            print("(error)", str(e))

        # Fine with answer
        else:
            write_result(answer)


RAW_HELP = """
Use raw formatting for replies (default when STDOUT is not a tty). \
However, you can use --no-raw to force formatted output even \
when STDOUT is not a tty.
"""
DECODE_HELP = (
    "decode response, defult is No decode, which will output all bytes literals."
)
NO_INFO = """
By default iredis will fire a INFO command to get redis-server's \
version, but you can use this flag to disable it."""


# command line entry here...
@click.command()
@click.pass_context
@click.option("-h", help="Server hostname (default: 127.0.0.1).", default="127.0.0.1")
@click.option("-p", help="Server port (default: 6379).", default="6379")
@click.option("-n", help="Database number.", default=None)
@click.option("-a", "--password", help="Password to use when connecting to the server.")
@click.option("--raw/--no-raw", default=False, is_flag=True, help=RAW_HELP)
@click.option("--no-info", default=False, is_flag=True, help=NO_INFO)
@click.option(
    "--newbie/--no-newbie",
    default=False,
    is_flag=True,
    help="Show command hints and useful helps.",
)
@click.option("--decode", default=None, help=DECODE_HELP)
@click.version_option()
@click.argument("cmd", nargs=-1)
def gather_args(ctx, h, p, n, password, raw, cmd, decode, newbie, no_info):
    """
    IRedis: Interactive Redis

    When no command is given, redis-cli starts in interactive mode.

    \b
    Examples:
      - iredis
      - iredis -h 127.0.0.1 -p 6379
      - iredis -h 127.0.0.1 -p 6379 -a <password>

    Type "help" in interactive mode for information on available commands
    and settings.
    """
    logger.info(
        f"[start args] host={h}, port={p}, db={n}, raw={raw}, cmd={cmd}, decode={decode}."
    )
    # figout raw output or formatted output
    if ctx.get_parameter_source("raw") == click.ParameterSource.COMMANDLINE:
        config.raw = raw
    else:
        if sys.stdout.isatty():
            config.raw = False
        else:
            config.raw = True
    # set config decode
    config.decode = decode
    config.newbie_mode = newbie

    return ctx


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
    client = Client(
        ctx.params["h"],
        ctx.params["p"],
        ctx.params["n"],
        ctx.params["password"],
        config.decode,
        get_info=not ctx.params["no_info"],
    )
    if not sys.stdin.isatty():
        for line in sys.stdin.readlines():
            logger.debug(f"[Command stdin] {line}")
            answer = client.send_command(line, None)
            write_result(answer)
        return

    if ctx.params["cmd"]:  # no interactive mode
        answer = client.send_command(" ".join(ctx.params["cmd"]), None)
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
    )
    compile_grammar_bg(session)

    # print hello message
    greetings()
    repl(client, session, enter_main_time)
