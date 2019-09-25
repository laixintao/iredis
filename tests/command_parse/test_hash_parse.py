def test_hdel(judge_command):
    judge_command(
        "HDEL foo bar", {"command_key_fields": "HDEL", "key": "foo", "fields": "bar"}
    )
    judge_command(
        "HDEL foo bar hello world",
        {"command_key_fields": "HDEL", "key": "foo", "fields": "bar hello world"},
    )
