import logging
from typing import Iterable

import pendulum
from prompt_toolkit.completion import (
    CompleteEvent,
    Completer,
    Completion,
    FuzzyWordCompleter,
    WordCompleter,
)
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.document import Document

from .commands import split_command_args, commands_summary, all_commands
from .config import config
from .exceptions import InvalidArguments, AmbiguousCommand
from .redis_grammar import CONST, command_grammar, get_command_grammar
from .utils import strip_quote_args, ensure_str

logger = logging.getLogger(__name__)


class MostRecentlyUsedFirstWordMixin:
    """
    A Mixin for WordCompleter, with a `touch()` method can make latest used
    word appears first. And evict old completion word when `max_words` reached.

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


class MostRecentlyUsedFirstWordCompleter(
    MostRecentlyUsedFirstWordMixin, FuzzyWordCompleter
):
    pass


class IntegerTypeCompleter(MostRecentlyUsedFirstWordMixin, WordCompleter):
    def __init__(self):
        words = []
        for i in range(1, 64):
            words.append(f"i{i}")  # signed integer, 64 bit max
            words.append(f"u{i}")  # unsigned integer, 63 bit max
        words.append("i64")
        super().__init__(len(words), list(reversed(words)))


class TimestampCompleter(Completer):
    """
    Completer for timestamp based on input.

    Features:
    * Auto complete humanize time, like 3 -> 3 minutes ago, 3 hours ago.
    * Auto guess datetime, complete by its timestamp. 2020-01-01 12:00
        -> 1577851200.

    The timezone is read from system.
    """

    when_lower_than = {
        "year": 20,
        "month": 12,
        "day": 31,
        "hour": 100,
        "minute": 1000,
        "second": 1000_000,
    }

    def _completion_humanize_time(self, document: Document) -> Iterable[Completion]:
        text = document.text
        if not text.isnumeric():
            return
        current = int(text)
        now = pendulum.now()
        for unit, minium in self.when_lower_than.items():
            if current <= minium:
                dt = now.subtract(**{f"{unit}s": current})
                meta = f"{text} {unit}{'s' if current > 1 else ''} ago ({dt.format('YYYY-MM-DD HH:mm:ss')})"
                yield Completion(
                    str(dt.int_timestamp * 1000),
                    start_position=-len(document.text_before_cursor),
                    display_meta=meta,
                )

    def _completion_formatted_time(self, document: Document) -> Iterable[Completion]:
        text = document.text
        try:
            dt = pendulum.parse(text)
        except Exception:
            return
        yield Completion(
            str(dt.int_timestamp * 1000),
            start_position=-len(document.text_before_cursor),
            display_meta=str(dt),
        )

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        completions = list(self._completion_humanize_time(document)) + list(
            self._completion_formatted_time(document)
        )

        # here we yield bigger timestamp first.
        for completion in sorted(completions, key=lambda a: a.text):
            yield completion


class IRedisCompleter(Completer):
    """
    Completer class that can dynamically returns any Completer.

    :param get_completer: Callable that returns a :class:`.Completer` instance.
    """

    def __init__(self, hint=False, completion_casing="upper"):
        super().__init__()
        self.completer_mapping = self.get_completer_mapping(hint, completion_casing)
        self.current_completer = self.root_completer = GrammarCompleter(
            command_grammar, self.completer_mapping
        )

    @property
    def key_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["key"]

    @property
    def member_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["member"]

    @property
    def field_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["field"]

    @property
    def group_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["group"]

    @property
    def catetoryname_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["categoryname"]

    @property
    def username_completer(self) -> MostRecentlyUsedFirstWordCompleter:
        return self.completer_mapping["username"]

    def get_completer(self, input_text):
        try:
            command, _ = split_command_args(input_text)
            # here will compile grammar for this command
            grammar = get_command_grammar(command)
            completer = GrammarCompleter(
                compiled_grammar=grammar, completers=self.completer_mapping
            )
        except (InvalidArguments, AmbiguousCommand):
            completer = self.root_completer

        return completer

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        input_text = document.text
        self.current_completer = self.get_completer(input_text)
        return self.current_completer.get_completions(document, complete_event)

    def update_completer_for_input(self, command):
        completer = self.get_completer(command)
        grammar = completer.compiled_grammar
        m = grammar.match(command)
        if not m:
            # invalid command!
            return
        variables = m.variables()

        # auto update completion words, if it's LRU strategy.
        for _token, _completer in self.completer_mapping.items():
            if not isinstance(_completer, MostRecentlyUsedFirstWordMixin):
                continue

            # getall always returns a []
            tokens_in_command = variables.getall(_token)
            for _token_in_command in tokens_in_command:
                # prompt_toolkit didn't support multi tokens
                # like DEL key1 key2 key3
                # so we have to split them manualy
                for single_token in strip_quote_args(_token_in_command):
                    _completer.touch(single_token)

    def update_completer_for_response(self, command_name, args, response):
        command_name = " ".join(command_name.split()).upper()
        logger.info(
            f"Try update completer using response... command_name is {command_name}"
        )
        if response is None:
            return

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

        if command_name in ("SCAN",):
            self.key_completer.touch_words(response[1])
            logger.debug(f"[Completer] key completer updated with {response[1]}.")

        if command_name in ("SSCAN", "ZSCAN"):
            self.member_completer.touch_words(response[1])
            logger.debug(f"[Completer] member completer updated with {response[1]}.")

        if command_name in ("HSCAN",):
            self.field_completer.touch_words(response[1][::2])
            logger.debug(
                f"[Completer] field completer updated with {response[1][::2]}."
            )

        # only update categoryname completer when `ACL CAT` without args.
        if command_name == "ACL CAT" and not args:
            self.catetoryname_completer.touch_words(response)
        if command_name == "ACL USERS":
            self.username_completer.touch_words(response)

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

    def get_completer_mapping(self, hint_on, completion_casing):
        completer_mapping = {}
        completer_mapping.update(
            {
                key: WordCompleter(tokens.split(" "), ignore_case=True)
                for key, tokens in CONST.items()
            }
        )
        key_completer = MostRecentlyUsedFirstWordCompleter(config.completer_max, [])
        member_completer = MostRecentlyUsedFirstWordCompleter(config.completer_max, [])
        field_completer = MostRecentlyUsedFirstWordCompleter(config.completer_max, [])
        group_completer = MostRecentlyUsedFirstWordCompleter(config.completer_max, [])
        username_completer = MostRecentlyUsedFirstWordCompleter(
            config.completer_max, []
        )
        categoryname_completer = MostRecentlyUsedFirstWordCompleter(100, [])
        timestamp_completer = TimestampCompleter()
        integer_type_completer = IntegerTypeCompleter()

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
                # zmember
                # TODO sperate sorted set and set
                # hash fields
                "field": field_completer,
                "fields": field_completer,
                # stream groups
                "group": group_completer,
                # stream id
                "stream_id": timestamp_completer,
                "inttype": integer_type_completer,
                "categoryname": categoryname_completer,
                "username": username_completer,
            }
        )

        # command completer
        if hint_on:
            command_hint = {
                key: info["summary"] for key, info in commands_summary.items()
            }
            hint = {
                command: command_hint.get(command.upper()) for command in all_commands
            }
            hint.update(
                {
                    command.lower(): command_hint.get(command.upper())
                    for command in all_commands
                }
            )
        else:
            hint = {}

        upper_commands = all_commands[::-1]
        lower_commands = [command.lower() for command in all_commands[::-1]]
        auto_commands = upper_commands + lower_commands

        ignore_case = completion_casing != "auto"

        command_completions = {
            "auto": auto_commands,
            "upper": upper_commands,
            "lower": lower_commands,
        }.get(completion_casing)

        completer_mapping["command"] = WordCompleter(
            command_completions, ignore_case=ignore_case, sentence=True, meta_dict=hint
        )
        return completer_mapping
