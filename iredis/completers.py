import re
import time
import threading
import logging

from typing import Iterable
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.contrib.regular_languages.compiler import compile
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion, CompleteEvent

from .config import config, COMPILING_DONE, COMPILING_JUST_FINISH
from .redis_grammar import REDIS_COMMANDS
from .lexer import get_lexer
from .commands_csv_loader import group2commands


logger = logging.getLogger(__name__)
BLANK_RE = re.compile(r"\s")


class FakeDocument:
    pass


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
        if BLANK_RE.match(document.char_before_cursor):
            return []
        return super().get_completions(stripped, complete_event)

    def _remove_duplicates(self, items):
        """
        Redis grammar guarantee that no completers will be duplicated"""
        return items


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
        time.sleep(1)
        config.compiling = COMPILING_DONE

    compiling_thread = threading.Thread(target=compile_and_patch, args=(session,))
    compiling_thread.start()
