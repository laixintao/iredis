import pytest


def test_client_setname(judge_command):
    judge_command(
        "CLIENT SETNAME foobar", {"command_value": "CLIENT SETNAME", "value": "foobar"}
    )


def test_client_unblock(judge_command):
    judge_command(
        "CLIENT UNBLOCK 33 TIMEOUT",
        {
            "command_clientid_errorx": "CLIENT UNBLOCK",
            "clientid": "33",
            "error": "TIMEOUT",
        },
    )
    judge_command(
        "CLIENT UNBLOCK 33",
        {"command_clientid_errorx": "CLIENT UNBLOCK", "clientid": "33"},
    )


def test_flushdb(judge_command):
    judge_command("FLUSHDB", {"command_asyncx": "FLUSHDB"})
    judge_command("FLUSHDB async", {"command_asyncx": "FLUSHDB", "async": "async"})
    judge_command("FLUSHDB ASYNC", {"command_asyncx": "FLUSHDB", "async": "ASYNC"})
    judge_command("FLUSHALL ASYNC", {"command_asyncx": "FLUSHALL", "async": "ASYNC"})


def test_client_list(judge_command):
    judge_command("client list", {"command_type_conntype_x": "client list"})
    judge_command("client list TYPE REPLICA1", None)
    judge_command(
        "client list type master",
        {
            "command_type_conntype_x": "client list",
            "type_const": "type",
            "conntype": "master",
        },
    )
    judge_command(
        "client list TYPE REPLICA",
        {
            "command_type_conntype_x": "client list",
            "type_const": "TYPE",
            "conntype": "REPLICA",
        },
    )


def test_configset(judge_command):
    judge_command(
        "config set foo bar",
        {"command_parameter_value": "config set", "parameter": "foo", "value": "bar"},
    )
    judge_command(
        "config set requirepass ''",
        {
            "command_parameter_value": "config set",
            "parameter": "requirepass",
            "value": "''",
        },
    )


def test_shutdown(judge_command):
    judge_command("shutdown save", {"command_shutdown": "shutdown", "shutdown": "save"})
    judge_command(
        "shutdown NOSAVE", {"command_shutdown": "shutdown", "shutdown": "NOSAVE"}
    )


def test_clientpause(judge_command):
    judge_command(
        "client pause 3000", {"command_timeout": "client pause", "timeout": "3000"}
    )


def test_client_reply(judge_command):
    judge_command("client reply on", {"command_switch": "client reply", "switch": "on"})


def test_client_kill(judge_command):
    judge_command(
        "CLIENT KILL addr 127.0.0.1:12345 type pubsub",
        {
            "command_clientkill": "CLIENT KILL",
            "addr": "addr",
            "ip_port": "127.0.0.1:12345",
            "type_const": "type",
            "conntype": "pubsub",
        },
    )
    judge_command(
        "CLIENT KILL 127.0.0.1:12345 ",
        {"command_clientkill": "CLIENT KILL", "ip_port": "127.0.0.1:12345"},
    )
    judge_command(
        "CLIENT KILL id 123455 type pubsub skipme no",
        {
            "command_clientkill": "CLIENT KILL",
            "const_id": "id",
            "clientid": "123455",
            "type_const": "type",
            "conntype": "pubsub",
            "skipme": "skipme",
            "yes": "no",
        },
    )


@pytest.mark.xfail(reason="currently no support arbitrary ordered command args")
def test_client_kill_unordered_arguments(judge_command):
    judge_command(
        "CLIENT KILL type pubsub addr 127.0.0.1:12345",
        {
            "command_clientkill": "CLIENT KILL",
            "addr": "addr",
            "ip_port": "127.0.0.1:12345",
            "type_const": "type",
            "conntype": "pubsub",
        },
    )
