from unittest.mock import MagicMock, patch

import pendulum
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter
from prompt_toolkit.completion import Completion

from iredis.completers import LatestUsedFirstWordCompleter
from iredis.redis_grammar import command_grammar
from iredis.completers import (
    get_completer_mapping,
    IRedisCompleter,
    TimestampCompleter,
    IntegerTypeCompleter,
)


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
    completer = IRedisCompleter(hint=False)
    completions = list(completer.get_completions(fake_document, None))
    assert [word.text for word in completions] == ["GEORADIUS", "GEORADIUSBYMEMBER"]
    assert [word.display_meta for word in completions] == [
        FormattedText([("", "")]),
        FormattedText([("", "")]),
    ]


def test_newbie_mode_complete_with_meta_dict():
    fake_document = MagicMock()
    fake_document.text_before_cursor = "GEOR"
    completer = IRedisCompleter(hint=True)
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


def test_iredis_completer_update_for_response():
    c = IRedisCompleter()
    c.update_completer_for_response(
        "HGETALL",
        [
            b"Behave",
            b"misbehave",
            b"Interpret",
            b"misinterpret",
            b"Lead",
            b"mislead",
            b"Trust",
            b"mistrust",
        ],
    )
    assert c.field_completer.words == ["Trust", "Lead", "Interpret", "Behave"]


def test_iredis_completer_no_exception_for_none_response():
    c = IRedisCompleter()
    c.update_completer_for_response("XPENDING", None)
    c.update_completer_for_response("KEYS", None)


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

    # No plural
    fake_document.text = fake_document.text_before_cursor = "1"
    completions = list(c.get_completions(fake_document, None))

    assert completions == [
        Completion(
            text="1546951013000",
            start_position=-1,
            display=FormattedText([("", "1546951013000")]),
            display_meta="1 year ago (2019-01-08 12:36:53)",
        ),
        Completion(
            text="1575808613000",
            start_position=-1,
            display=FormattedText([("", "1575808613000")]),
            display_meta="1 month ago (2019-12-08 12:36:53)",
        ),
        Completion(
            text="1578400613000",
            start_position=-1,
            display=FormattedText([("", "1578400613000")]),
            display_meta="1 day ago (2020-01-07 12:36:53)",
        ),
        Completion(
            text="1578483413000",
            start_position=-1,
            display=FormattedText([("", "1578483413000")]),
            display_meta="1 hour ago (2020-01-08 11:36:53)",
        ),
        Completion(
            text="1578486953000",
            start_position=-1,
            display=FormattedText([("", "1578486953000")]),
            display_meta="1 minute ago (2020-01-08 12:35:53)",
        ),
        Completion(
            text="1578487012000",
            start_position=-1,
            display=FormattedText([("", "1578487012000")]),
            display_meta="1 second ago (2020-01-08 12:36:52)",
        ),
    ]


def test_timestamp_completer_datetime_format_time_completion():
    c = TimestampCompleter()
    fake_document = MagicMock()
    fake_document.text = fake_document.text_before_cursor = "2020-02-07"
    completions = list(c.get_completions(fake_document, None))

    assert completions == [
        Completion(
            text="1581033600000",
            start_position=-10,
            display=FormattedText([("", "1581033600000")]),
            display_meta="2020-02-07T00:00:00+00:00",
        )
    ]


def test_integer_type_completer():
    c = IntegerTypeCompleter()
    fake_document = MagicMock()
    fake_document.text = fake_document.get_word_before_cursor.return_value = "i"
    completions = list(c.get_completions(fake_document, None))
    assert len(completions) == 64

    fake_document.text = fake_document.get_word_before_cursor.return_value = "u"
    completions = list(c.get_completions(fake_document, None))
    assert len(completions) == 63

    c.touch("u4")
    assert list(c.get_completions(fake_document, None))[0].text == "u4"
