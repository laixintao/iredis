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
