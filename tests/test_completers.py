import time
import threading
from unittest.mock import MagicMock
from prompt_toolkit.completion import Completion
from prompt_toolkit.formatted_text import FormattedText

from iredis.completers import LatestUsedFirstWordCompleter
from iredis.config import config
from iredis.entry import compile_grammar_bg
from .conftest import prompt_session


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
    config.newbie_mode = False
    session = prompt_session()
    fake_document = MagicMock()
    fake_document.text_before_cursor = "get"
    completions = list(session.completer.get_completions(fake_document, None))
    assert completions == [
        Completion(
            text="get",
            start_position=-3,
            display=FormattedText([("", "get")]),
            display_meta=FormattedText([("", "")]),
        ),
        Completion(
            text="getset",
            start_position=-3,
            display=FormattedText([("", "getset")]),
            display_meta=FormattedText([("", "")]),
        ),
        Completion(
            text="getrange",
            start_position=-3,
            display=FormattedText([("", "getrange")]),
            display_meta=FormattedText([("", "")]),
        ),
        Completion(
            text="getbit",
            start_position=-3,
            display=FormattedText([("", "getbit")]),
            display_meta=FormattedText([("", "")]),
        ),
    ]


def test_newbie_mode_complete_with_meta_dict():
    config.newbie_mode = True
    session = prompt_session()
    fake_document = MagicMock()
    fake_document.text_before_cursor = "get"
    completions = list(session.completer.get_completions(fake_document, None))

    assert completions[:2] == [
        Completion(
            text="get",
            start_position=-3,
            display=FormattedText([("", "get")]),
            display_meta=FormattedText([("", "Get the value of a key")]),
        ),
        Completion(
            text="getset",
            start_position=-3,
            display=FormattedText([("", "getset")]),
            display_meta=FormattedText(
                [("", "Set the string value of a key and return its old value")]
            ),
        ),
    ]


def test_patch_grammer_and_session_after_startup():
    session = MagicMock()
    normal_thread_count = threading.active_count()
    session.lexer = None
    session.completer = None
    compile_grammar_bg(session)
    assert session.lexer is None
    assert session.completer is None
    assert threading.active_count() == normal_thread_count + 1

    while threading.active_count() > normal_thread_count:
        time.sleep(0.1)
    assert session.lexer
    assert session.completer
