from unittest.mock import Mock

import pytest

from iredis import entry


@pytest.fixture
def client_from_args(monkeypatch, tmp_path, config):
    config_file = tmp_path / "iredisrc"
    config_file.write_text(
        "[main]\nlog_location =\n[alias_dsn]\n" "local = redis://localhost:6379/5\n"
    )
    monkeypatch.delenv("IREDIS_URL", raising=False)
    monkeypatch.delenv("IREDIS_DSN", raising=False)
    client = Mock()
    monkeypatch.setattr(entry, "Client", client)

    def create(args):
        ctx = entry.gather_args.main(
            ["--iredisrc", str(config_file), *args], standalone_mode=False
        )
        entry.create_client(ctx.params)
        return client.call_args.kwargs

    return create


@pytest.mark.parametrize(
    "connection_args",
    [
        ["--url", "redis://localhost:6379/5"],
        ["--url", "rediss://localhost:6379/5"],
        ["--url", "unix:///tmp/redis.sock?db=5"],
        ["--dsn", "local"],
    ],
)
@pytest.mark.parametrize("database", [None, 0, 3])
def test_database_override_for_urls_and_dsns(
    client_from_args, connection_args, database
):
    args = connection_args.copy()
    if database is not None:
        args.extend(["-n", str(database)])

    params = client_from_args(args)

    assert params["db"] == (5 if database is None else database)


@pytest.mark.parametrize("connection_args", [[], ["--socket", "/tmp/redis.sock"]])
@pytest.mark.parametrize("database", [None, 0, 3])
def test_database_for_direct_connections(client_from_args, connection_args, database):
    args = connection_args.copy()
    if database is not None:
        args.extend(["-n", str(database)])

    params = client_from_args(args)

    assert params["db"] == (0 if database is None else database)


def test_database_zero_overrides_url_from_environment(client_from_args, monkeypatch):
    monkeypatch.setenv("IREDIS_URL", "redis://localhost:6379/5")

    assert client_from_args(["-n", "0"])["db"] == 0


def test_database_zero_overrides_dsn_from_environment(client_from_args, monkeypatch):
    monkeypatch.setenv("IREDIS_DSN", "local")

    assert client_from_args(["-n", "0"])["db"] == 0
