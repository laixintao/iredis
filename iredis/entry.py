# -*- coding: utf-8 -*-
import os
import sys
import logging
import time
import threading
from pathlib import Path
from typing import Dict, Iterable, List


import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.document import Document
from prompt_toolkit.contrib.regular_languages.compiler import compile
from prompt_toolkit.completion import Completion, CompleteEvent
from prompt_toolkit import print_formatted_text

from .client import Client
from .renders import render_dict
from .redis_grammar import REDIS_COMMANDS
from .commands_csv_loader import group2commands, group2command_res
from .utils import timer, literal_bytes
from .style import STYLE
from .config import config

logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".iredis_history"


class FakeDocument:
    pass


class RedisGrammarCompleter(GrammarCompleter):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        origin_text = document.text_before_cursor
        stripped = FakeDocument()
        stripped.text_before_cursor = origin_text.lstrip()
        # Do not complete on spaces, too slow
        if not origin_text.strip():
            return []
        return super().get_completions(stripped, complete_event)


def get_lexer(command_groups, redis_grammar):
    lexers_dict = {
        "key": SimpleLexer("class:key"),
        "keys": SimpleLexer("class:key"),
        "index": SimpleLexer("class:integer"),
        "password": SimpleLexer("class:password"),
    }
    lexers_dict.update(
        {key: SimpleLexer("class:pygments.keyword") for key in command_groups}
    )
    lexer = GrammarLexer(redis_grammar, lexers=lexers_dict)
    return lexer


def get_completer(group2commands, redis_grammar):
    completer_mapping = {
        command_group: WordCompleter(
            commands + [command.lower() for command in commands], sentence=True
        )
        for command_group, commands in group2commands.items()
    }
    completer_mapping.update(
        {"failoverchoice": WordCompleter(["TAKEOVER", "FORCE", "takeover", "force"])}
    )
    completer = RedisGrammarCompleter(redis_grammar, completer_mapping)
    return completer


def compile_grammar_bg(session):
    """
    compile redis grammar in a thread, and patch session's lexer
    and completer.
    """

    def compile_and_patch(session):
        start_time = time.time()
        logger.debug("[compile] start compile grammer...")
        redis_grammar = compile(REDIS_COMMANDS)
        end_time = time.time()
        logger.debug(f"[compile] Compile finished! Cost: {end_time - start_time}")

        # get lexer
        lexer = get_lexer(group2commands.keys(), redis_grammar)
        # get completer
        completer = get_completer(group2commands, redis_grammar)

        session.completer = completer
        session.lexer = lexer
        logger.debug("[compile] Patch finished!")

    compiling_thread = threading.Thread(target=compile_and_patch, args=(session,))
    compiling_thread.start()


def write_result(text):
    """
    :param text: is_raw: bytes, not raw: FormattedText
    :is_raw: bool
    """
    if config.raw:
        sys.stdout.buffer.write(text)
        sys.stdout.write("\n")
    else:
        print_formatted_text(text, end="")


def repl(client, session):
    is_raw = config.raw
    timer(f"First REPL command enter, is_raw={is_raw}.")
    while True:
        logger.info("↓↓↓↓" * 10)
        logger.info("REPL waiting for command...")
        try:
            command = session.prompt("{hostname}> ".format(hostname=str(client)))

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
Use raw formatting for replies (default when STDOUT is not a tty). However, you can use --no-raw to force formatted output even when STDOUT is not a tty.
"""
# command line entry here...
@click.command(
    help="""When no command is given, redis-cli starts in interactive mode."""
)
@click.pass_context
@click.option("-h", help="Server hostname", default="127.0.0.1")
@click.option("-p", help="Server port", default="6379")
@click.option("-n", help="Database number.", default=None)
@click.option("--raw/--no-raw", default=False, is_flag=True, help=RAW_HELP)
@click.argument("cmd", nargs=-1)
def gather_args(ctx, h, p, n, raw, cmd):
    logger.info(f"[start args] host={h}, port={p}, db={n}, raw={raw}, cmd={cmd}.")
    # figout raw output or formatted output
    if ctx.get_parameter_source("raw") == click.ParameterSource.COMMANDLINE:
        config.raw = raw
    else:
        if sys.stdout.isatty():
            config.raw = False
        else:
            config.raw = True
    logger.debug(f"[Config] Is raw output? {config.raw}")
    return ctx


def main():
    enter_main_time = time.time()
    # invoke in non-standalone mode to gather args
    ctx = gather_args.main(standalone_mode=False)
    if not ctx:  # called help
        return
    # redis client
    client = Client(ctx.params["h"], ctx.params["p"], ctx.params["n"])
    if not sys.stdin.isatty():
        for line in sys.stdin.readlines():
            logger.debug(f"[Command stdin] {line}")
            answer = client.send_command(line, None)
            write_result(answer)
        return

    if ctx.params["cmd"]:  # no interactive mode
        answer = client.send_command(" ".join(ctx.params["cmd"]), None)
        write_result(answer)
        logger.warn("[OVER] command executed, exit...")
        return

    # Create history file if not exists.
    if not os.path.exists(HISTORY_FILE):
        logger.info(f"History file {HISTORY_FILE} not exists, create now...")
        f = open(HISTORY_FILE, "w+")
        f.close()

    style = STYLE
    # prompt session
    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        style=style,
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True,
        complete_in_thread=True,
    )

    compile_grammar_bg(session)
    repl(client, session)
