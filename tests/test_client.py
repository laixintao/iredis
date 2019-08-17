import pytest
from unittest.mock import MagicMock, patch
from iredis.client import Client


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
    ],
)
def test_stipe_quote_escaple_in_quote(test_input, expected):
    client = Client("127.0.0.1", "6379", None)
    assert list(client._strip_quote_args(test_input)) == expected


@pytest.mark.parametrize(
    "_input, command_name, expect_args",
    [
        ("keys *", "keys", ["*"]),
        ("DEL abc foo bar", "DEL", ["abc", "foo", "bar"]),
        ("cluster info", "cluster info", []),
        ("CLUSTER failover FORCE", "CLUSTER failover", ["FORCE"]),
    ],
)
def test_send_command(_input, command_name, expect_args):
    client = Client("127.0.0.1", "6379", None)
    client.execute_command = MagicMock()
    client.send_command(_input)
    args, kwargs = client.execute_command.call_args
    assert args == (command_name, *expect_args)
