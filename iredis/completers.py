import logging
from typing import AsyncGenerator, Callable, Iterable, Optional, Sequence

from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    DummyCompleter,
    FuzzyWordCompleter,
    WordCompleter,
)
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.document import Document

from .commands_csv_loader import all_commands, commands_summary
from .config import config
from .exceptions import InvalidArguments
from .redis_grammar import CONST, command_grammar, get_command_grammar
from .utils import _strip_quote_args, split_command_args, ensure_str

logger = logging.getLogger(__name__)


class LatestUsedFirstWordCompleter(FuzzyWordCompleter):
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
        if word in self.words:
            self.words.remove(word)
        else:  # not in words
            if len(self.words) == self.max_words:  # full
                self.words.pop()
        self.words.insert(0, word)

    def touch_words(self, words):
        for word in words:
            self.touch(word)


def get_completer_mapping():
    completer_mapping = {}
    completer_mapping.update(
        {
            key: WordCompleter(tokens.split(" "), ignore_case=True)
            for key, tokens in CONST.items()
        }
    )
    key_completer = LatestUsedFirstWordCompleter(config.completer_max, [])
    member_completer = LatestUsedFirstWordCompleter(config.completer_max, [])
    field_completer = LatestUsedFirstWordCompleter(config.completer_max, [])

    completer_mapping.update(
        {
            # all key related completers share the same completer
            "keys": key_completer,
            "key": key_completer,
            "destination": key_completer,
            "newkey": key_completer,
            # member
            "member": member_completer,
            "members": member_completer,
            # hash fields
            "field": field_completer,
            "fields": field_completer,
        }
    )
    # patch command completer with hint
    command_hint = {key: info["summary"] for key, info in commands_summary.items()}
    hint = {command: command_hint.get(command.upper()) for command in all_commands}

    completer_mapping["command_pending"] = WordCompleter(
        all_commands[::-1], ignore_case=True, sentence=True, meta_dict=hint
    )
    return completer_mapping


completer_mapping = get_completer_mapping()


class IRedisCompleter(Completer):
    """
    Completer class that can dynamically returns any Completer.

    :param get_completer: Callable that returns a :class:`.Completer` instance.
    """

    def __init__(self):
        super().__init__()
        self.current_completer = self.root_completer = GrammarCompleter(
            command_grammar, completer_mapping
        )
        self.completer_mapping = completer_mapping

    @property
    def key_completer(self) -> LatestUsedFirstWordCompleter:
        return self.completer_mapping["key"]

    @property
    def member_completer(self) -> LatestUsedFirstWordCompleter:
        return self.completer_mapping["member"]

    @property
    def field_completer(self) -> LatestUsedFirstWordCompleter:
        return self.completer_mapping["field"]

    def get_completer(self, input_text):
        try:
            command, _ = split_command_args(input_text, all_commands)
            # compile grammar for this command
            grammar = get_command_grammar(command)
            completer = GrammarCompleter(
                compiled_grammar=grammar, completers=completer_mapping
            )
        except InvalidArguments:
            completer = self.root_completer

        return completer

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        input_text = document.text
        self.current_completer = self.get_completer(input_text)
        return self.current_completer.get_completions(document, complete_event)

    def touch_all_words(self, command):
        completer = self.get_completer(command)
        grammar = completer.compiled_grammar
        m = grammar.match(command)
        if not m:
            # invalide command!
            return
        variables = m.variables()

        # auto update LatestUsedFirstWordCompleter
        for _token, _completer in self.completer_mapping.items():
            if not isinstance(_completer, LatestUsedFirstWordCompleter):
                continue

            # getall always returns a []
            tokens_in_command = variables.getall(_token)
            for tokens_in_command in tokens_in_command:
                # prompt_toolkit didn't support multi tokens
                # like DEL key1 key2 key3
                # so we have to split them manualy
                for single_token in _strip_quote_args(tokens_in_command):
                    _completer.touch(single_token)

    def touch(self, command_name, response):
        command_name = command_name.upper()
        response = ensure_str(response)
        if command_name in ("HKEYS",):
            self.field_completer.touch_words(response)
            logger.debug(f"[Completer] field completer updated with {response}.")

        if command_name in ("HGETALL",):
            self.field_completer.touch_words(response[::2])
            logger.debug(f"[Completer] field completer updated with {response[::2]}.")

        if command_name in ("ZPOPMAX", "ZPOPMIN", "ZRANGE", "ZRANGE", "ZRANGEBYSCORE"):
            if config.withscores:
                self.member_completer.touch_words(response[::2])
                logger.debug(
                    f"[Completer] member completer updated with {response[::2]}."
                )
            else:
                self.member_completer.touch_words(response)
                logger.debug(f"[Completer] member completer updated with {response}.")

        if command_name in ("KEYS",):
            self.key_completer.touch_words(response)
            logger.debug(f"[Completer] key completer updated with {response}.")

    def _touch_members(self, items):
        _step = 1

        if config.withscores:
            _step = 2

        self.member_completer.touch_words(ensure_str(items)[::_step])

    def _touch_hash_pairs(self, items):
        self.field_completer.touch_words(ensure_str(items)[::2])

    def _touch_keys(self, items):
        self.key_completer.touch_words(ensure_str(items))

    def __repr__(self) -> str:
        return "DynamicCompleter(%r -> %r)" % (
            self.get_completer,
            self.current_completer,
        )


class IRedisGrammarCompleter(Completer):
    def __init__(self):
        super().__init__(command_grammar, completer_mapping)

    @property
    def key_completer(self):
        return self.completers["key"]

    @property
    def member_completer(self):
        return self.completers["member"]

    @property
    def field_completer(self):
        return self.completers["field"]


default_completer = IRedisCompleter()
