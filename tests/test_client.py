import pytest
from unittest.mock import MagicMock
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
    client.execute_command_and_read_response = MagicMock()
    client.send_command(_input, None)
    args, kwargs = client.execute_command_and_read_response.call_args
    assert args == (None, command_name, *expect_args)


def test_patch_completer(completer):
    client = Client("127.0.0.1", "6379", None)
    client.pre_hook(
        "MGET foo bar hello world", "MGET", "foo bar hello world", completer
    )
    assert completer.completers["key"].words == ["world", "hello", "bar", "foo"]
    assert completer.completers["keys"].words == ["world", "hello", "bar", "foo"]
    client.pre_hook("GET bar", "GET", "bar", completer)
    assert completer.completers["keys"].words == ["bar", "world", "hello", "foo"]


def test_get_server_verison_after_client():
    from iredis.config import config

    Client("127.0.0.1", "6379", None)
    assert config.version.startswith("5.")

    config.version = "Unknown"
    Client("127.0.0.1", "6379", None, get_info=False)
    assert config.version == "Unknown"


def test_do_help():
    from iredis.config import config

    client = Client("127.0.0.1", "6379", None)
    config.version = "5.0.0"
    resp = client.do_help("SET")
    assert resp[10] == ("", "1.0.0 (Avaiable, redis-server: 5.0.0)")
    config.version = "2.0.0"
    resp = client.do_help("cluster", "addslots")
    assert resp[10] == ("", "3.0.0 (Not avaiable, redis-server: 2.0.0)")
