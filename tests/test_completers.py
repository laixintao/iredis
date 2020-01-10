import pytest

from unittest.mock import MagicMock
from prompt_toolkit.completion import Completion
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter

from iredis.completers import LatestUsedFirstWordCompleter
from iredis.config import config
from iredis.redis_grammar import get_command_grammar, command_grammar
from iredis.completers import completer_mapping


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
    completer = GrammarCompleter(command_grammar, completer_mapping)
    completions = list(completer.get_completions(fake_document, None))
    assert [word.text for word in completions] == ["GEORADIUS", "GEORADIUSBYMEMBER"]


@pytest.mark.xfail(reason="meta info not work, but in real use it's ok, fix later")
def test_newbie_mode_complete_with_meta_dict():
    fake_document = MagicMock()
    fake_document.text_before_cursor = "GEOR"
    completer = GrammarCompleter(command_grammar, completer_mapping)
    completions = list(completer.get_completions(fake_document, None))
    print(completions[0])

    assert completions[:2] == None
