import pytest
import redis
from unittest.mock import MagicMock

from prompt_toolkit.formatted_text import FormattedText

from iredis.client import Client
from iredis.completers import IRedisCompleter
from iredis.entry import Rainbow, prompt_message


@pytest.fixture
def completer():
    return IRedisCompleter()


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
    client.execute = MagicMock()
    next(client.send_command(_input, None))
    args, kwargs = client.execute.call_args
    assert args == (command_name, *expect_args)


def test_patch_completer():
    client = Client("127.0.0.1", "6379", None)
    completer = IRedisCompleter()
    client.pre_hook(
        "MGET foo bar hello world", "MGET", "foo bar hello world", completer
    )
    assert completer.key_completer.words == ["world", "hello", "bar", "foo"]
    assert completer.key_completer.words == ["world", "hello", "bar", "foo"]

    client.pre_hook("GET bar", "GET", "bar", completer)
    assert completer.key_completer.words == ["bar", "world", "hello", "foo"]


def test_get_server_verison_after_client(config):
    Client("127.0.0.1", "6379", None)
    assert config.version.startswith("5.")

    config.version = "Unknown"
    config.no_info = True
    Client("127.0.0.1", "6379", None)
    assert config.version == "Unknown"


def test_do_help(config):
    client = Client("127.0.0.1", "6379", None)
    config.version = "5.0.0"
    resp = client.do_help("SET")
    assert resp[10] == ("", "1.0.0 (Avaiable on your redis-server: 5.0.0)")
    config.version = "2.0.0"
    resp = client.do_help("cluster", "addslots")
    assert resp[10] == ("", "3.0.0 (Not avaiable on your redis-server: 2.0.0)")


def test_rainbow_iterator():
    "test color infinite iterator"
    original_color = Rainbow.color
    Rainbow.color = list(range(0, 3))
    assert list(zip(range(10), Rainbow())) == [
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 1),
        (4, 0),
        (5, 1),
        (6, 2),
        (7, 1),
        (8, 0),
        (9, 1),
    ]
    Rainbow.color = original_color


def test_prompt_message(iredis_client, config):
    config.rainbow = False
    assert prompt_message(iredis_client) == "127.0.0.1:6379[15]> "

    config.rainbow = True
    assert prompt_message(iredis_client)[:3] == [
        ("#cc2244", "1"),
        ("#bb4444", "2"),
        ("#996644", "7"),
    ]


def test_on_connection_error_retry(iredis_client, config):
    config.retry_times = 1
    mock_connection = MagicMock()
    mock_connection.read_response.side_effect = [
        redis.exceptions.ConnectionError(
            "Error 61 connecting to 127.0.0.1:7788. Connection refused."
        ),
        "hello",
    ]
    original_connection = iredis_client.connection
    iredis_client.connection = mock_connection
    value = iredis_client.execute("None", "GET", ["foo"])
    assert value == "hello"  # be rendered

    mock_connection.disconnect.assert_called_once()
    mock_connection.connect.assert_called_once()

    iredis_client.connection = original_connection


def test_on_connection_error_retry_without_retrytimes(iredis_client, config):
    config.retry_times = 0
    mock_connection = MagicMock()
    mock_connection.read_response.side_effect = [
        redis.exceptions.ConnectionError(
            "Error 61 connecting to 127.0.0.1:7788. Connection refused."
        ),
        "hello",
    ]
    iredis_client.connection = mock_connection
    with pytest.raises(redis.exceptions.ConnectionError):
        iredis_client.execute("None", "GET", ["foo"])

    mock_connection.disconnect.assert_not_called()
    mock_connection.connect.assert_not_called()


def test_socket_keepalive(config):
    config.socket_keepalive = True
    from iredis.client import Client

    newclient = Client("127.0.0.1", "6379", 0)
    assert newclient.connection.socket_keepalive

    # keepalive off
    config.socket_keepalive = False

    newclient = Client("127.0.0.1", "6379", 0)
    assert not newclient.connection.socket_keepalive


def test_not_retry_on_authentication_error(iredis_client, config):
    config.retry_times = 2
    mock_connection = MagicMock()
    mock_connection.read_response.side_effect = [
        redis.exceptions.AuthenticationError("Authentication required."),
        "hello",
    ]
    iredis_client.connection = mock_connection
    with pytest.raises(redis.exceptions.ConnectionError):
        iredis_client.execute("None", "GET", ["foo"])


def test_auto_select_db_and_auth_for_reconnect(iredis_client, config):
    config.retry_times = 2
    config.raw = True
    next(iredis_client.send_command("select 2"))
    assert iredis_client.connection.db == 2

    resp = next(iredis_client.send_command("auth 123"))
    assert "Client sent AUTH, but no password is set" in resp
    assert iredis_client.connection.password is None

    next(iredis_client.send_command("config set requirepass 'abc'"))
    next(iredis_client.send_command("auth abc"))
    assert iredis_client.connection.password == "abc"
    next(iredis_client.send_command("config set requirepass ''"))


def test_split_shell_command(iredis_client, completer):
    assert iredis_client.split_command_and_pipeline(" get json | rg . ", completer) == (
        " get json ",
        "rg . ",
    )

    assert iredis_client.split_command_and_pipeline(
        """ get "json | \\" hello" | rg . """, completer
    ) == (""" get "json | \\" hello" """, "rg . ")


def test_running_with_pipeline(clean_redis, iredis_client, capfd, completer):
    clean_redis.set("foo", "hello \n world")
    with pytest.raises(StopIteration):
        next(iredis_client.send_command("get foo | grep w", completer))
    out, err = capfd.readouterr()
    assert out == " world\n"


def test_running_with_multiple_pipeline(clean_redis, iredis_client, capfd, completer):
    clean_redis.set("foo", "hello world\nhello iredis")
    with pytest.raises(StopIteration):
        next(
            iredis_client.send_command("get foo | grep hello | grep iredis", completer)
        )
    out, err = capfd.readouterr()
    assert out == "hello iredis\n"


def test_can_not_connect_on_startup(capfd):
    Client("localhost", "16111", 15)
    out, err = capfd.readouterr()
    assert "connecting to localhost:16111." in err


def test_peek_non_exist(iredis_client, clean_redis, config):
    config.raw = False
    peek_result = list(iredis_client.do_peek("non-exist-key"))
    assert peek_result == [FormattedText([("class:dockey", "type: "), ("", "none")])]


def test_peek_string(iredis_client, clean_redis):
    clean_redis.set("foo", "bar")
    peek_result = list(iredis_client.do_peek("foo"))

    assert peek_result == [
        FormattedText([("class:dockey", "type: "), ("", "string")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "embstr")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "50")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
        FormattedText([("class:dockey", "strlen: "), ("", "3")]),
        FormattedText([("class:dockey", "value: "), ("", '"bar"')]),
    ]


def test_peek_list_fetch_all(iredis_client, clean_redis):
    clean_redis.lpush("mylist", *[f"hello-{index}" for index in range(5)])
    peek_result = list(iredis_client.do_peek("mylist"))

    assert peek_result == [
        FormattedText([("class:dockey", "type: "), ("", "list")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "quicklist")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "176")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
        FormattedText([("class:dockey", "llen: "), ("", "5")]),
        FormattedText([("class:dockey", "elements: ")]),
        FormattedText(
            [
                ("", "1)"),
                ("", " "),
                ("class:string", '"hello-4"'),
                ("", "\n"),
                ("", "2)"),
                ("", " "),
                ("class:string", '"hello-3"'),
                ("", "\n"),
                ("", "3)"),
                ("", " "),
                ("class:string", '"hello-2"'),
                ("", "\n"),
                ("", "4)"),
                ("", " "),
                ("class:string", '"hello-1"'),
                ("", "\n"),
                ("", "5)"),
                ("", " "),
                ("class:string", '"hello-0"'),
            ]
        ),
    ]


def test_peek_list_fetch_part(iredis_client, clean_redis):
    clean_redis.lpush("mylist", *[f"hello-{index}" for index in range(40)])
    peek_result = list(iredis_client.do_peek("mylist"))
    print(peek_result)
    assert len(peek_result[6]) == 83


def test_peek_set_fetch_all(iredis_client, clean_redis):
    clean_redis.sadd("myset", *[f"hello-{index}" for index in range(5)])
    peek_result = list(iredis_client.do_peek("myset"))

    assert peek_result[0:6] == [
        FormattedText([("class:dockey", "type: "), ("", "set")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "hashtable")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "404")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
        FormattedText([("class:dockey", "cardinality: "), ("", "5")]),
        FormattedText([("class:dockey", "members: ")]),
    ]


def test_peek_set_fetch_part(iredis_client, clean_redis):
    clean_redis.sadd("myset", *[f"hello-{index}" for index in range(40)])
    peek_result = list(iredis_client.do_peek("myset"))

    assert ("class:member", '"hello-1"') in peek_result[6]
    assert ("class:member", '"hello-10"') in peek_result[6]


def test_peek_zset_fetch_all(iredis_client, clean_redis):
    clean_redis.zadd(
        "myzset", dict(zip([f"hello-{index}" for index in range(3)], range(3)))
    )
    peek_result = list(iredis_client.do_peek("myzset"))
    assert peek_result == [
        FormattedText([("class:dockey", "type: "), ("", "zset")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "ziplist")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "92")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
        FormattedText([("class:dockey", "zcount: "), ("", "3")]),
        FormattedText([("class:dockey", "members: ")]),
        FormattedText(
            [
                ("", "1)"),
                ("", " "),
                ("class:member", '"hello-0"'),
                ("", "\n"),
                ("", "2)"),
                ("", " "),
                ("class:member", '"0"'),
                ("", "\n"),
                ("", "3)"),
                ("", " "),
                ("class:member", '"hello-1"'),
                ("", "\n"),
                ("", "4)"),
                ("", " "),
                ("class:member", '"1"'),
                ("", "\n"),
                ("", "5)"),
                ("", " "),
                ("class:member", '"hello-2"'),
                ("", "\n"),
                ("", "6)"),
                ("", " "),
                ("class:member", '"2"'),
            ]
        ),
    ]


def test_peek_zset_fetch_part(iredis_client, clean_redis):
    clean_redis.zadd(
        "myzset", dict(zip([f"hello-{index}" for index in range(40)], range(40)))
    )
    peek_result = list(iredis_client.do_peek("myzset"))
    assert len(peek_result[6]) == 199


def test_peek_hash_fetch_all(iredis_client, clean_redis):
    for key, value in zip(
        [f"hello-{index}" for index in range(3)], [f"hi-{index}" for index in range(3)]
    ):
        clean_redis.hset("myhash", key, value)
    peek_result = list(iredis_client.do_peek("myhash"))
    assert peek_result == [
        FormattedText([("class:dockey", "type: "), ("", "hash")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "ziplist")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "104")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
        FormattedText([("class:dockey", "hlen: "), ("", "3")]),
        FormattedText([("class:dockey", "fields: ")]),
        FormattedText(
            [
                ("", "1)"),
                ("", " "),
                ("class:field", '"hello-0"'),
                ("", "\n"),
                ("", "   "),
                ("class:string", '"hi-0"'),
                ("", "\n"),
                ("", "2)"),
                ("", " "),
                ("class:field", '"hello-1"'),
                ("", "\n"),
                ("", "   "),
                ("class:string", '"hi-1"'),
                ("", "\n"),
                ("", "3)"),
                ("", " "),
                ("class:field", '"hello-2"'),
                ("", "\n"),
                ("", "   "),
                ("class:string", '"hi-2"'),
            ]
        ),
    ]


def test_peek_hash_fetch_part(iredis_client, clean_redis):
    for key, value in zip(
        [f"hello-{index}" for index in range(100)],
        [f"hi-{index}" for index in range(100)],
    ):
        clean_redis.hset("myhash", key, value)
    peek_result = list(iredis_client.do_peek("myhash"))
    assert ("class:string", '"hi-10"') in peek_result[6]
    assert ("class:field", '"hello-10"') in peek_result[6]


def test_peek_stream(iredis_client, clean_redis):
    clean_redis.xadd("mystream", {"foo": "bar", "hello": "world"})
    peek_result = list(iredis_client.do_peek("mystream"))
    print(peek_result)
    assert peek_result[0:4] == [
        FormattedText([("class:dockey", "type: "), ("", "stream")]),
        FormattedText([("class:dockey", "object encoding: "), ("", "unknown")]),
        FormattedText([("class:dockey", "memory usage(bytes): "), ("", "601")]),
        FormattedText([("class:dockey", "ttl: "), ("", "-1")]),
    ]
    assert ("class:string", '"length"') in peek_result[5]
    assert ("class:string", '"radix-tree-keys"') in peek_result[5]
