import pytest
from iredis.client import Client

client = Client("127.0.0.1", "6379", None)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("hello world", ["hello", "world"]),
        ("'hello world'", ["hello world"]),
        ('''hello"world"''', ["helloworld"]),
        (r'''hello\"world"''', [r"hello\world"]),
        (r'"\\"', [r"\\"]),
        (r"\abcd ef", [r"\abcd", "ef"]),
        (r""" 'hello"world' """, ['hello"world']),
        (r""" "hello'world" """, ["hello'world"]),
    ],
)
def test_stipe_quote_escaple_in_quote(test_input, expected):
    assert list(client._strip_quote_args(test_input)) == expected
