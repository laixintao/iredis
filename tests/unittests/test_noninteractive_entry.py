from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from iredis import entry


@pytest.mark.parametrize("stdin_is_tty", [False, True])
def test_explicit_command_does_not_read_stdin(monkeypatch, stdin_is_tty):
    stdin = Mock()
    stdin.isatty.return_value = stdin_is_tty
    stdin.readlines.side_effect = AssertionError("stdin should not be read")
    monkeypatch.setattr(entry.sys, "stdin", stdin)
    monkeypatch.setattr(
        entry.gather_args,
        "main",
        Mock(return_value=SimpleNamespace(params={"cmd": ("PING",)})),
    )
    client = Mock()
    client.send_command.return_value = [b"PONG"]
    monkeypatch.setattr(entry, "create_client", Mock(return_value=client))
    write_result = Mock()
    monkeypatch.setattr(entry, "write_result", write_result)

    entry.main()

    client.send_command.assert_called_once_with("PING", None)
    write_result.assert_called_once_with(b"PONG")


def test_stdin_commands_without_explicit_command(monkeypatch):
    monkeypatch.setattr(entry.sys, "stdin", StringIO("PING\nECHO hello\n"))
    monkeypatch.setattr(
        entry.gather_args,
        "main",
        Mock(return_value=SimpleNamespace(params={"cmd": ()})),
    )
    client = Mock()
    client.send_command.side_effect = [[b"PONG"], [b"hello"]]
    monkeypatch.setattr(entry, "create_client", Mock(return_value=client))
    write_result = Mock()
    monkeypatch.setattr(entry, "write_result", write_result)

    entry.main()

    assert client.send_command.call_args_list == [
        call("PING\n", None),
        call("ECHO hello\n", None),
    ]
    assert write_result.call_args_list == [call(b"PONG"), call(b"hello")]
