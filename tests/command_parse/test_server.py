def test_client_setname(judge_command):
    judge_command(
        "CLIENT SETNAME foobar", {"command_value": "CLIENT SETNAME", "value": "foobar"}
    )
