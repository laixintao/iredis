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


class LatestUsedFirstWordCompleter(WordCompleter):
    """
    Not thread safe.
    """

    def __init__(self, max_words, words, *args, **kwargs):
        self.words = words
        self.max_words = max_words
        super().__init__(words, *args, **kwargs)

    def touch(self, word):
        """
        Make sure word is in the first place of the completer
        list.
        """
        logger.info(f"[LRU]: {self.words} ++ {word}")
        if word in self.words:
            self.words.remove(word)
        else:  # not in words
            if len(self.words) == self.max_words:  # full
                self.words.pop()
        self.words.insert(0, word)
        logger.info(f"[LRU] Done: {self.words}")

    def touch_words(self, words):
        for word in words:
            self.touch(word)


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
        if not origin_text.strip():
            return []
        return super().get_completions(stripped, complete_event)


def get_completer(group2commands, redis_grammar):
    completer_mapping = {
        command_group: WordCompleter(
            commands + [command.lower() for command in commands], sentence=True
        )
        for command_group, commands in group2commands.items()
    }
    keys_completer = LatestUsedFirstWordCompleter(config.completer_max, [])
    completer_mapping.update(
        {
            "failoverchoice": WordCompleter(["TAKEOVER", "FORCE", "takeover", "force"]),
            "keys": keys_completer,
            "key": keys_completer,  # key and keys are the same
        }
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
