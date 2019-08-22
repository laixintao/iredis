import pytest
from unittest.mock import MagicMock, patch
from iredis.client import Client

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
    client.send_command(_input, None)
    args, kwargs = client.execute_command.call_args
    assert args == (None, command_name, *expect_args)
