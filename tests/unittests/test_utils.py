import re
import time
import pytest
from unittest.mock import patch

from iredis.utils import timer, strip_quote_args
from iredis.commands import split_command_args, split_unknown_args
from iredis.utils import command_syntax, parse_argument_to_formatted_text, compose_command_syntax
from iredis.style import STYLE
from iredis.exceptions import InvalidArguments, AmbiguousCommand
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
        (r"\\", ["\\\\"]),  # backslash are legal
        ("\\hello\\", ["\\hello\\"]),  # backslash are legal
        ('foo "bar\\n1"', ["foo", "bar\n1"]),
    ],
)
def test_stripe_quote_escape_in_quote(test_input, expected):
    assert list(strip_quote_args(test_input)) == expected


@pytest.mark.parametrize(
    "command,expected,args",
    [
        ("GET a", "GET", ["a"]),
        ("cluster info", "cluster info", []),
        ("getbit foo 17", "getbit", ["foo", "17"]),
        ("command ", "command", []),
        (" command count  ", "command count", []),
        (" command  count  ", "command  count", []),  # command with multi space
        (" command  count    ' hello   world'", "command  count", [" hello   world"]),
        ("set foo 'hello   world'", "set", ["foo", "hello   world"]),
    ],
)
def test_split_commands(command, expected, args):
    parsed_command, parsed_args = split_command_args(command)
    assert expected == parsed_command
    assert args == parsed_args


def test_split_commands_fail_on_unknown_command():
    with pytest.raises(InvalidArguments):
        split_command_args("FOO BAR")


@pytest.mark.parametrize(
    "command",
    ["command in", "command   in", "Command   in", "COMMAND     in"],
)
def test_split_commands_fail_on_partially_input(command):
    with pytest.raises(AmbiguousCommand):
        split_command_args(command)


def test_split_commands_fail_on_unfinished_command():
    with pytest.raises(InvalidArguments):
        split_command_args("setn")


def test_render_bottom_with_command_json():
    for command, info in commands_summary.items():
        print_formatted_text(command_syntax(command, info), style=STYLE)


@pytest.mark.parametrize(
    "raw,command,args",
    [
        ("abc 123", "abc", ["123"]),
        ("abc", "abc", []),
        ("abc foo bar", "abc", ["foo", "bar"]),
        ("abc 'foo bar'", "abc", ["foo bar"]),
        ('abc "foo bar"', "abc", ["foo bar"]),
        ('abc "foo bar" 3 hello', "abc", ["foo bar", "3", "hello"]),
        ('abc "foo \nbar"', "abc", ["foo \nbar"]),
    ],
)
def test_split_unknown_commands(raw, command, args):
    parsed_command, parsed_args = split_unknown_args(raw)
    assert command == parsed_command
    assert args == parsed_args


class TestParseArgumentToFormattedText:
    """Tests for parse_argument_to_formatted_text function."""

    def test_simple_argument_without_token(self):
        """Test argument without token."""
        result = parse_argument_to_formatted_text("cursor", "integer", False)
        assert len(result) == 1
        assert result[0][1] == " cursor"

    def test_optional_argument_without_token(self):
        """Test optional argument without token."""
        result = parse_argument_to_formatted_text("key", "key", True)
        assert len(result) == 1
        assert result[0][1] == " [key]"

    def test_argument_with_token(self):
        """Test argument with token (like MATCH pattern)."""
        result = parse_argument_to_formatted_text("pattern", "pattern", False, token="MATCH")
        assert len(result) == 1
        assert result[0][1] == " MATCH pattern"

    def test_optional_argument_with_token(self):
        """Test optional argument with token (like [MATCH pattern])."""
        result = parse_argument_to_formatted_text("pattern", "pattern", True, token="MATCH")
        assert len(result) == 1
        assert result[0][1] == " [MATCH pattern]"

    def test_multiple_tokens(self):
        """Test multiple arguments with different tokens."""
        result1 = parse_argument_to_formatted_text("pattern", "pattern", True, token="MATCH")
        result2 = parse_argument_to_formatted_text("count", "integer", True, token="COUNT")
        result3 = parse_argument_to_formatted_text("type", "string", True, token="TYPE")
        
        assert result1[0][1] == " [MATCH pattern]"
        assert result2[0][1] == " [COUNT count]"
        assert result3[0][1] == " [TYPE type]"


class TestComposeCommandSyntax:
    """Tests for compose_command_syntax function."""

    def test_scan_command_syntax(self):
        """Test SCAN command shows correct syntax with tokens."""
        scan_info = {
            "arguments": [
                {"name": "cursor", "type": "integer"},
                {"name": "pattern", "type": "pattern", "token": "MATCH", "optional": True},
                {"name": "count", "type": "integer", "token": "COUNT", "optional": True},
                {"name": "type", "type": "string", "token": "TYPE", "optional": True},
            ]
        }
        result = compose_command_syntax(scan_info)
        text = "".join([t[1] for t in result])
        
        assert "cursor" in text
        assert "[MATCH pattern]" in text
        assert "[COUNT count]" in text
        assert "[TYPE type]" in text

    def test_hscan_command_syntax(self):
        """Test HSCAN command shows correct syntax with tokens."""
        hscan_info = {
            "arguments": [
                {"name": "key", "type": "key"},
                {"name": "cursor", "type": "integer"},
                {"name": "pattern", "type": "pattern", "token": "MATCH", "optional": True},
                {"name": "count", "type": "integer", "token": "COUNT", "optional": True},
            ]
        }
        result = compose_command_syntax(hscan_info)
        text = "".join([t[1] for t in result])
        
        assert "key" in text
        assert "cursor" in text
        assert "[MATCH pattern]" in text
        assert "[COUNT count]" in text

    def test_command_without_tokens(self):
        """Test command without any tokens."""
        get_info = {
            "arguments": [
                {"name": "key", "type": "key"},
            ]
        }
        result = compose_command_syntax(get_info)
        text = "".join([t[1] for t in result])
        
        assert "key" in text
        assert "MATCH" not in text

    def test_real_scan_command_from_commands_summary(self):
        """Test real SCAN command from commands_summary."""
        scan_info = commands_summary["SCAN"]
        result = compose_command_syntax(scan_info)
        text = "".join([t[1] for t in result])
        
        assert "[MATCH pattern]" in text
        assert "[COUNT count]" in text
        assert "[TYPE type]" in text
