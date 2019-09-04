def test_sadd(judge_command):
    judge_command(
        "SADD foo m1 m2 m3",
        {"command_key_members": "SADD", "key": "foo", "members": "m1 m2 m3"},
    )
