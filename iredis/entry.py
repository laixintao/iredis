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
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
    TransformationInput,
)

from .client import Client
from .redis_grammar import REDIS_COMMANDS
from .commands_csv_loader import (
    group2commands,
    group2command_res,
    all_commands,
    commands_summary,
)
from .utils import timer, literal_bytes, split_command_args, command_syntax
from .style import STYLE
from .config import config, COMPILING_IN_PROGRESS, COMPILING_DONE, COMPILING_JUST_FINISH
from iredis.exceptions import InvalidArguments

logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".iredis_history"


class FakeDocument:
    pass


class UserInputCommand:
    """
    User inputted command in real time.

    ``RedisGrammarCompleter`` update it, and ``BottomToolbar`` read it
    """

    def __init__(self):
        # command will always be upper case
        self.command = None


class RedisGrammarCompleter(GrammarCompleter):
    """
    This disable Completer on blank characters, blank char will cause
    performance issues.
    """

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


class GetCommandProcessor(Processor):
    """
    Update Footer display text while user input.
    """

    def __init__(self, command_holder):
        self.last_text = None
        self.command_holder = command_holder

    def apply_transformation(
        self, transformation_input: TransformationInput
    ) -> Transformation:
        input_text = transformation_input.document.text
        if input_text != self.last_text:
            logger.debug(f"[Processor] {transformation_input.document}")
            try:
                command, _ = split_command_args(input_text, all_commands)
            except InvalidArguments:
                logger.debug(f"[Processor] Redis command not recongnised!")
                self.command_holder.command = None
            else:
                logger.debug(f"[Processor] Redis command: {command}")
                self.command_holder.command = command.upper()

            self.last_text = input_text
        return Transformation(transformation_input.fragments)


def get_lexer(command_groups, redis_grammar):
    # pygments token
    # http://pygments.org/docs/tokens/
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

        config.compiling = COMPILING_JUST_FINISH
        time.sleep(2)
        config.compiling = COMPILING_DONE

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
        print_formatted_text()


class BottomToolbar:
    CHAR = "⣾⣷⣯⣟⡿⢿⣻⣽"

    def __init__(self, command_holder):
        self.index = 0
        # BottomToolbar can only read this variable
        self.command_holder = command_holder

    def get_animation_char(self):
        animation = self.CHAR[self.index]

        self.index += 1
        if self.index == len(self.CHAR):
            self.index = 0
        return animation

    def render(self):
        if config.compiling == COMPILING_IN_PROGRESS:
            anim = self.get_animation_char()
            loading_text = (
                "class:bottom-toolbar.off",
                f"Loading Redis commands {anim}\n",
            )
        elif config.compiling == COMPILING_JUST_FINISH:
            loading_text = (
                "class:bottom-toolbar.loaded",
                f"Redis commands loaded! Auto Completer activated!\n",
            )
        else:
            loading_text = ("class:bottom-toolbar", "")
        bottoms = [loading_text]

        # add command help if valide
        if self.command_holder.command:
            command_info = commands_summary[self.command_holder.command]
            hint = command_syntax(self.command_holder.command, command_info)

        return bottoms


def repl(client, session):
    is_raw = config.raw
    command_holder = UserInputCommand()
    timer(f"First REPL command enter, is_raw={is_raw}.")
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
Use raw formatting for replies (default when STDOUT is not a tty). However, you can use --no-raw to force formatted output even when STDOUT is not a tty.
"""
DECODE_HELP = (
    "decode response, defult is No decode, which will output all bytes literals."
)
# command line entry here...
@click.command(
    help="""When no command is given, redis-cli starts in interactive mode."""
)
@click.pass_context
@click.option("-h", help="Server hostname", default="127.0.0.1")
@click.option("-p", help="Server port", default="6379")
@click.option("-n", help="Database number.", default=None)
@click.option("--raw/--no-raw", default=False, is_flag=True, help=RAW_HELP)
@click.option("--decode", default=None, help=DECODE_HELP)
@click.argument("cmd", nargs=-1)
def gather_args(ctx, h, p, n, raw, cmd, decode):
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

    logger.debug(f"[Config] Is raw output? {config.raw}")
    logger.debug(f"[Config] Decode option: {config.decode}")
    return ctx


def main():
    enter_main_time = time.time()
    # invoke in non-standalone mode to gather args
    ctx = gather_args.main(standalone_mode=False)
    if not ctx:  # called help
        return
    # redis client
    client = Client(ctx.params["h"], ctx.params["p"], ctx.params["n"], config.decode)
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
    )

    compile_grammar_bg(session)
    repl(client, session)
