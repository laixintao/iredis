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
