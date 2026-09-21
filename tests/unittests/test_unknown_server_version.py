from unittest.mock import Mock

import pytest
from prompt_toolkit.formatted_text import to_plain_text

from iredis.client import Client
from iredis.renders import OutputRender


@pytest.mark.parametrize("version", ["Unknown", None, "", "custom-redis"])
def test_peek_without_server_version(config, version):
    config.version = version
    replies = {
        "type": b"string",
        "object encoding": b"embstr",
        "ttl": -1,
        "strlen": 3,
        "GET": b"bar",
    }
    client = Mock(spec=Client)
    client.execute.side_effect = lambda command, *args: replies[command]

    result = list(Client.do_peek(client, "foo"))

    assert to_plain_text(result[0]) == (
        'key: string (embstr), ttl: -1\nstrlen: 3\nvalue: "bar"'
    )


@pytest.mark.parametrize("version", ["Unknown", None, "", "4.0.0", "7.2.0"])
@pytest.mark.parametrize("with_client_info", [False, True])
def test_slowlog_uses_reply_fields_without_server_version(
    config, version, with_client_info
):
    config.version = version
    reply = [1, 1700000000, 42, [b"GET", b"foo"]]
    if with_client_info:
        reply.extend([b"127.0.0.1:12345", b"worker"])

    result = to_plain_text(OutputRender.render_slowlog([reply]))

    assert "Slow log id: 1" in result
    assert "Command: GET foo" in result
    assert ("Client IP and port: 127.0.0.1:12345" in result) == with_client_info
    assert ("Client name: worker" in result) == with_client_info


def test_empty_slowlog_without_server_version(config):
    assert OutputRender.render_slowlog([]) == []
