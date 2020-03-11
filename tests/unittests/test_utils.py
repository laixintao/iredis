import re
import time
import pytest
from unittest.mock import patch

from iredis.utils import timer, strip_quote_args
from iredis.commands import split_command_args
from iredis.utils import command_syntax
from iredis.style import STYLE
from iredis.commands import commands_summary
from prompt_toolkit import print_formatted_text


def test_timer():
    with patch("iredis.utils.logger") as mock_logger:
        timer("foo")
        time.sleep(0.1)
        timer("bar")
        mock_logger.debug.assert_called()
        args, kwargs = mock_logger.debug.call_args
        matched = re.match(r"\[timer (\d)\] (0\.\d+) -> bar", args[0])

        assert matched.group(1) == str(3)
        assert 0.1 <= float(matched.group(2)) <= 0.2

        # --- test again ---
        timer("foo")
        time.sleep(0.2)
        timer("bar")
        mock_logger.debug.assert_called()
        args, kwargs = mock_logger.debug.call_args
        matched = re.match(r"\[timer (\d)\] (0\.\d+) -> bar", args[0])

        assert matched.group(1) == str(5)
        assert 0.2 <= float(matched.group(2)) <= 0.3


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("hello world", ["hello", "world"]),
        ("'hello world'", ["hello world"]),
        ('''hello"world"''', ["helloworld"]),
        (r'''hello\"world"''', [r"hello\world"]),
        (r'"\\"', [r"\\"]),
        (r"\\", [r"\\"]),
        (r"\abcd ef", [r"\abcd", "ef"]),
        # quotes in quotes
        (r""" 'hello"world' """, ['hello"world']),
        (r""" "hello'world" """, ["hello'world"]),
        (r""" 'hello\'world'""", ["hello'world"]),
        (r""" "hello\"world" """, ['hello"world']),
        (r"''", [""]),  # set foo "" is a legal command
        (r'""', [""]),  # set foo "" is a legal command
        (r"\\", ["\\\\"]),  # blackslash are legal
        ("\\hello\\", ["\\hello\\"]),  # blackslash are legal
    ],
)
def test_stipe_quote_escaple_in_quote(test_input, expected):
    assert list(strip_quote_args(test_input)) == expected


@pytest.mark.parametrize(
    "command,expected",
    [
        ("GET a", "GET"),
        ("cluster info", "cluster info"),
        ("getbit foo 17", "getbit"),
        ("command ", "command"),
        (" command count  ", "command count"),
        (" command  count  ", "command count"),  # command with multi space
    ],
)
def test_split_commands(command, expected):
    assert split_command_args(command)[0] == expected


def test_render_bottom_with_command_json():
    for command, info in commands_summary.items():
        print_formatted_text(command_syntax(command, info), style=STYLE)
