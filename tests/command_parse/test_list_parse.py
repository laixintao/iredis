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


def test_lindex(judge_command):
    judge_command(
        "LINDEX list1 10",
        {"command_key_position": "LINDEX", "key": "list1", "position": "10"},
    )
    judge_command(
        "LINDEX list1 -10",
        {"command_key_position": "LINDEX", "key": "list1", "position": "-10"},
    )
    judge_command("LINDEX list1 1.1", None)
