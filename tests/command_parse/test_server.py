def test_client_setname(judge_command):
    judge_command(
        "CLIENT SETNAME foobar", {"command_value": "CLIENT SETNAME", "value": "foobar"}
    )


def test_client_unblock(judge_command):
    judge_command(
        "CLIENT UNBLOCK 33 TIMEOUT",
        {"command_value": "CLIENT UNBLOCK", "clientid": "33", "error": "TIMEOUT"},
    )
    judge_command(
        "CLIENT UNBLOCK 33", {"command_value": "CLIENT UNBLOCK", "clientid": "33"}
    )
