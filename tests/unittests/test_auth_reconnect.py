from unittest.mock import MagicMock, patch

import pytest
from redis.exceptions import AuthenticationError, ResponseError

from iredis.client import Client
from iredis.commands import command2syntax


@pytest.fixture
def auth_client(config, monkeypatch):
    config.no_info = True
    config.raw = True
    config.warning = False
    config.shell = True
    config.transaction = False
    config.version = "7.2"
    config.alias_dsn = {}
    monkeypatch.setitem(command2syntax, "AUTH", "command_usernamex_password")
    # These tests never connect to Redis.  Use a non-default port as an extra
    # safeguard, including for the connection created by build_connection().
    with patch("redis.connection.Connection.connect"):
        client = Client("127.0.0.1", 1, username="original", password="old-secret")
        client.execute = MagicMock(return_value=b"OK")
        yield client


def credentials(client):
    return (
        client.username,
        client.password,
        client.connection.username,
        client.connection.password,
    )


@pytest.mark.parametrize(
    "command,username,password",
    [
        ("AUTH alice new-secret", "alice", "new-secret"),
        ("AUTH new-secret", None, "new-secret"),
        ('AUTH alice "two words"', "alice", "two words"),
        ('AUTH alice ""', "alice", ""),
        ('AUTH ""', None, ""),
    ],
)
def test_successful_auth_updates_reconnection_credentials(
    auth_client, command, username, password
):
    assert list(auth_client.send_command(command)) == [b"OK"]
    assert credentials(auth_client) == (username, password, username, password)
    auth_client.build_connection()
    assert credentials(auth_client) == (username, password, username, password)


def test_failed_auth_preserves_reconnection_credentials(auth_client):
    before = credentials(auth_client)
    auth_client.execute.side_effect = AuthenticationError("invalid credentials")
    result = list(auth_client.send_command("AUTH alice wrong-secret"))
    assert result == [b"ERROR invalid credentials"]
    assert credentials(auth_client) == before


def test_queued_auth_does_not_change_credentials_or_select_database(auth_client):
    before = credentials(auth_client)
    auth_client.db = 3
    auth_client.execute.return_value = b"QUEUED"
    assert list(auth_client.send_command("AUTH alice new-secret")) == [b"QUEUED"]
    assert credentials(auth_client) == before
    auth_client.execute.assert_called_once_with("AUTH", "alice", "new-secret")


def test_accepted_auth_is_kept_when_database_reselection_fails(auth_client):
    auth_client.db = 3
    auth_client.execute.side_effect = [b"OK", ResponseError("SELECT denied")]
    assert list(auth_client.send_command("AUTH alice new-secret")) == [
        b"ERROR SELECT denied"
    ]
    assert credentials(auth_client) == ("alice", "new-secret", "alice", "new-secret")
    auth_client.build_connection()
    assert credentials(auth_client) == ("alice", "new-secret", "alice", "new-secret")


def test_redirect_uses_credentials_from_manual_auth(auth_client):
    list(auth_client.send_command("AUTH alice new-secret"))
    auth_client.execute_by_connection = MagicMock(return_value=b"PONG")
    assert auth_client.reissue_with_redirect("MOVED 1 127.0.0.1:2", "PING") == b"PONG"
    redirected = auth_client.execute_by_connection.call_args.args[0]
    assert (redirected.username, redirected.password) == ("alice", "new-secret")


@pytest.mark.parametrize(
    "command,expected_credentials,expected_db",
    [
        ("AUTH alice new-secret", ("alice", "new-secret", "alice", "new-secret"), 0),
        ("SELECT 3", ("original", "old-secret", "original", "old-secret"), 3),
    ],
)
def test_piped_commands_update_state_before_writing_payload(
    auth_client, command, expected_credentials, expected_db
):
    auth_client.split_command_and_pipeline = MagicMock(return_value=(command, "cat"))
    completer = MagicMock()
    with patch("iredis.client.run") as pipe:
        assert list(auth_client.send_command(command + " | cat", completer)) == []
    assert credentials(auth_client) == expected_credentials
    assert auth_client.db == expected_db
    assert auth_client.connection.db == expected_db
    pipe.assert_called_once_with("cat", input=b"OK", shell=True)
    completer.update_completer_for_response.assert_called_once()


def test_piped_binary_response_is_unchanged(auth_client):
    auth_client.split_command_and_pipeline = MagicMock(return_value=("GET key", "cat"))
    auth_client.execute.return_value = b"\xff\x00binary"
    with patch("iredis.client.run") as pipe:
        assert list(auth_client.send_command("GET key | cat", MagicMock())) == []
    pipe.assert_called_once_with("cat", input=b"\xff\x00binary", shell=True)


def test_failed_piped_auth_does_not_run_pipe_or_change_credentials(auth_client):
    before = credentials(auth_client)
    auth_client.split_command_and_pipeline = MagicMock(
        return_value=("AUTH alice wrong-secret", "cat")
    )
    auth_client.execute.side_effect = AuthenticationError("invalid credentials")
    with patch("iredis.client.run") as pipe:
        assert list(
            auth_client.send_command("AUTH alice wrong-secret | cat", MagicMock())
        ) == [b"ERROR invalid credentials"]
    pipe.assert_not_called()
    assert credentials(auth_client) == before


def test_queued_piped_select_does_not_change_database(auth_client, config):
    config.transaction = True
    auth_client.split_command_and_pipeline = MagicMock(return_value=("SELECT 3", "cat"))
    auth_client.execute.return_value = b"QUEUED"
    with patch("iredis.client.run") as pipe:
        assert list(auth_client.send_command("SELECT 3 | cat", MagicMock())) == []
    assert auth_client.db == 0
    assert auth_client.connection.db == 0
    pipe.assert_called_once_with("cat", input=b"QUEUED", shell=True)


@pytest.mark.parametrize("command", ["AUTH alice new-secret", "SELECT 3", "MULTI"])
def test_cancelled_commands_do_not_change_state(auth_client, command, capsys, config):
    before = credentials(auth_client)
    auth_client.execute = Client.execute.__get__(auth_client, Client)
    auth_client.connection.send_command = MagicMock()
    auth_client.connection.read_response = MagicMock(side_effect=KeyboardInterrupt)
    assert list(auth_client.send_command(command)) == [b""]
    assert credentials(auth_client) == before
    assert auth_client.db == 0
    assert auth_client.connection.db == 0
    assert config.transaction is False
    assert "User canceled reading response" in capsys.readouterr().err


def test_decoded_successful_auth_updates_credentials(auth_client):
    auth_client.execute.return_value = "OK"
    assert list(auth_client.send_command("AUTH alice new-secret")) == [b"OK"]
    assert credentials(auth_client) == ("alice", "new-secret", "alice", "new-secret")


def test_piped_multi_updates_transaction_state(auth_client, config):
    auth_client.split_command_and_pipeline = MagicMock(return_value=("MULTI", "cat"))
    with patch("iredis.client.run") as pipe:
        assert list(auth_client.send_command("MULTI | cat", MagicMock())) == []
    assert config.transaction is True
    pipe.assert_called_once_with("cat", input=b"OK", shell=True)


def test_cancelled_piped_multi_does_not_change_transaction_state(
    auth_client, config, capsys
):
    auth_client.execute = Client.execute.__get__(auth_client, Client)
    auth_client.connection.send_command = MagicMock()
    auth_client.connection.read_response = MagicMock(side_effect=KeyboardInterrupt)
    auth_client.split_command_and_pipeline = MagicMock(return_value=("MULTI", "cat"))
    with patch("iredis.client.run") as pipe:
        assert list(auth_client.send_command("MULTI | cat", MagicMock())) == []
    assert config.transaction is False
    assert "User canceled reading response" in capsys.readouterr().err
    pipe.assert_called_once_with("cat", input=b"", shell=True)
