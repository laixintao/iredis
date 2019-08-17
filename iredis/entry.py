# -*- coding: utf-8 -*-
import os
import sys
import logging
import time
import threading
from pathlib import Path

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.contrib.regular_languages.compiler import compile

from .client import Client
from .renders import render_dict
from .redis_grammar import REDIS_COMMANDS
from .commands_csv_loader import group2commands, group2command_res
from .utils import timer


logger = logging.getLogger(__name__)

HISTORY_FILE = Path(os.path.expanduser("~")) / ".iredis_history"


def get_style():
    return Style.from_dict(
        {
            # User input (default text).
            "": "",
            # Prompt.
            "hostname": "",
            "operator": "#33aa33 bold",
            "number": "#ff0000 bold",
            "trailing-input": "bg:#662222 #ffffff",
            "password": "hidden",
        }
    )


def get_lexer(command_groups, redis_grammar):
    lexers_dict = {
        "key": SimpleLexer("class:operator"),
        "value": SimpleLexer("class:number"),
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
    # TODO add key value completer
    completer_mapping.update(
        {"failoverchoice": WordCompleter(["TAKEOVER", "FORCE", "takeover", "force"])}
    )
    completer = GrammarCompleter(redis_grammar, completer_mapping)
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


def repl(client, session):
    style = get_style()
    compile_grammar_bg(session)
    while True:
        timer("REPL waiting for command...")
        try:
            command = session.prompt(
                "{hostname}> ".format(hostname=str(client)),
                style=style,
                auto_suggest=AutoSuggestFromHistory(),
            )

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt!")
            continue
        except EOFError:
            print("Goodbye!")
            sys.exit()
        logger.info(f"[Command] {command}")

        # blank input
        if not command:
            continue

        try:
            answer = client.send_command(command)
        # Error with previous command or exception
        except Exception as e:
            logger.exception(e)
            print("(error)", str(e))

        # Fine with answer
        else:
            print(answer)


# command line entry here...
@click.command()
@click.pass_context
@click.option("-h", help="Server hostname", default="127.0.0.1")
@click.option("-p", help="Server port", default="6379")
@click.option("-n", help="Database number.", default=None)
def gather_args(ctx, h, p, n):
    logger.info(f"iredis start, host={h}, port={p}, db={n}.")
    return ctx


def main():
    enter_main_time = time.time()
    # invoke in non-standalone mode to gather args
    ctx = gather_args.main(standalone_mode=False)
    if not ctx:  # called help
        return

    # Create history file if not exists.
    if not os.path.exists(HISTORY_FILE):
        logger.info(f"History file {HISTORY_FILE} not exists, create now...")
        f = open(HISTORY_FILE, "w+")
        f.close()

    # prompt session
    session = PromptSession(history=FileHistory(HISTORY_FILE))
    # redis client
    client = Client(**ctx.params)

    repl(client, session)
