def test_rpush(judge_command):
    judge_command(
        "RPUSH list1 foo bar hello world",
        {
            "command_key_values": "RPUSH",
            "key": "list1",
            "values": "foo bar hello world",
        },
    )
    judge_command(
        "LPUSH list1 foo",
        {"command_key_values": "LPUSH", "key": "list1", "values": "foo"},
    )
