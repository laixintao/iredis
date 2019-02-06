from unittest.mock import MagicMock
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter

from iredis.completers import LatestUsedFirstWordCompleter
from iredis.redis_grammar import command_grammar
from iredis.completers import get_completer_mapping, IRedisCompleter


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
    assert [completion.text for completion in completions] == ["hello", "world"]
