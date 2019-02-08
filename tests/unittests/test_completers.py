from unittest.mock import MagicMock, patch

import pendulum
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.completion import Completion

from iredis.completers import LatestUsedFirstWordCompleter
from iredis.redis_grammar import command_grammar
from iredis.completers import get_completer_mapping, IRedisCompleter, TimestampCompleter


def test_LUF_completer_touch():
    c = LatestUsedFirstWordCompleter(3, ["one", "two"])
    c.touch("hello")
    assert c.words == ["hello", "one", "two"]

    c.touch("foo")
    assert c.words == ["foo", "hello", "one"]

    c.touch("hello")
    assert c.words == ["hello", "foo", "one"]


def test_LUF_completer_touch_words():
    c = LatestUsedFirstWordCompleter(3, [])
    c.touch_words(["hello", "world", "foo", "bar"])
    assert c.words == ["bar", "foo", "world"]

    c.touch_words(["one", "two"])
    assert c.words == ["two", "one", "bar"]


def test_newbie_mode_complete_without_meta_dict():
    fake_document = MagicMock()
    fake_document.text_before_cursor = "GEOR"
    completer = GrammarCompleter(command_grammar, get_completer_mapping())
    completions = list(completer.get_completions(fake_document, None))
    assert [word.text for word in completions] == ["GEORADIUS", "GEORADIUSBYMEMBER"]


def test_newbie_mode_complete_with_meta_dict():
    fake_document = MagicMock()
    fake_document.text_before_cursor = "GEOR"
    completer = GrammarCompleter(command_grammar, get_completer_mapping())
    completions = list(completer.get_completions(fake_document, None))

    assert sorted([completion.display_meta for completion in completions]) == [
        FormattedText(
            [
                (
                    "",
                    "Query a sorted set representing a geospatial index to fetch members matching a given maximum distance from a member",  # noqa
                )
            ]
        ),
        FormattedText(
            [
                (
                    "",
                    "Query a sorted set representing a geospatial index to fetch members matching a given maximum distance from a point",  # noqa
                )
            ]
        ),
    ]


def test_group_completer():
    fake_document = MagicMock()
    previous_commands = ["xgroup create abc world 123", "xgroup setid abc hello 123"]
    fake_document.text = fake_document.text_before_cursor = "XGROUP DESTROY key "
    completer = IRedisCompleter()
    for command in previous_commands:
        completer.update_completer_for_input(command)
    completions = list(completer.get_completions(fake_document, None))
    assert completions == [
        Completion(
            text="hello",
            start_position=0,
            display=FormattedText([("", "hello")]),
            display_meta=FormattedText([("", "")]),
        ),
        Completion(
            text="world",
            start_position=0,
            display=FormattedText([("", "world")]),
            display_meta=FormattedText([("", "")]),
        ),
    ]


@patch("iredis.completers.pendulum.now")
def test_timestamp_completer_humanize_time_completion(fake_now):
    fake_now.return_value = pendulum.from_timestamp(1578487013)
    c = TimestampCompleter()

    fake_document = MagicMock()
    fake_document.text = fake_document.text_before_cursor = "30"
    completions = list(c.get_completions(fake_document, None))

    assert completions == [
        Completion(
            text="1575895013000",
            start_position=-2,
            display=FormattedText([("", "1575895013000")]),
            display_meta="30 days ago (2019-12-09 12:36:53)",
        ),
        Completion(
            text="1578379013000",
            start_position=-2,
            display=FormattedText([("", "1578379013000")]),
            display_meta="30 hours ago (2020-01-07 06:36:53)",
        ),
        Completion(
            text="1578485213000",
            start_position=-2,
            display=FormattedText([("", "1578485213000")]),
            display_meta="30 minutes ago (2020-01-08 12:06:53)",
        ),
        Completion(
            text="1578486983000",
            start_position=-2,
            display=FormattedText([("", "1578486983000")]),
            display_meta="30 seconds ago (2020-01-08 12:36:23)",
        ),
    ]
