import pytest
from iredis.client import Client

client = Client("127.0.0.1", "6379", None)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("hello world", "hello world"),
        ("'hello world'", "hello world"),
        ('''"hello" "world 1"''', "hello world 1"),
    ],
)
def test_stipe_quote_escaple_in_quote(test_input, expected):
    assert "".join(client._strip_quote_args(test_input)) == expected
