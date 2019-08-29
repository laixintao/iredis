def test_set(judge_command):
    judge_command(
        "SET abc bar",
        {"command_key_value_expiration_condition": "SET", "key": "abc", "value": "bar"},
    )
    judge_command(
        "SET abc bar EX 10",
        {
            "command_key_value_expiration_condition": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "EX 10",
        },
    )
    judge_command(
        "SET abc bar px 10000",
        {
            "command_key_value_expiration_condition": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px 10000",
        },
    )
    judge_command(
        "SET abc bar px 10000 nx",
        {
            "command_key_value_expiration_condition": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px 10000",
            "condition": "nx",
        },
    )
    judge_command(
        "SET abc bar px 10000 XX",
        {
            "command_key_value_expiration_condition": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px 10000",
            "condition": "XX",
        },
    )
    judge_command(
        "SET abc bar XX",
        {
            "command_key_value_expiration_condition": "SET",
            "key": "abc",
            "value": "bar",
            "condition": "XX",
        },
    )


def test_append(judge_command):
    judge_command(
        "append foo bar", {"command_key_value": "append", "key": "foo", "value": "bar"}
    )
    judge_command(
        "APPEND foo 'bar'",
        {"command_key_value": "APPEND", "key": "foo", "value": "'bar'"},
    )
    judge_command("APPEND foo", None)


def test_bitcount(judge_command):
    judge_command("bitcount foo", {"command_key_start_end": "bitcount", "key": "foo"})
    judge_command(
        "bitcount foo 1 5",
        {"command_key_start_end": "bitcount", "key": "foo", "start": "1", "end": "5"},
    )
    judge_command(
        "bitcount foo 1 -5",
        {"command_key_start_end": "bitcount", "key": "foo", "start": "1", "end": "-5"},
    )
    judge_command(
        "bitcount foo -2 -1",
        {"command_key_start_end": "bitcount", "key": "foo", "start": "-2", "end": "-1"},
    )
    judge_command("bitcount foo -2", None)
