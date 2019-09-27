def test_hdel(judge_command):
    judge_command(
        "HDEL foo bar", {"command_key_fields": "HDEL", "key": "foo", "fields": "bar"}
    )
    judge_command(
        "HDEL foo bar hello world",
        {"command_key_fields": "HDEL", "key": "foo", "fields": "bar hello world"},
    )


def test_hmset(judge_command):
    judge_command(
        "HMSET foo bar hello-world",
        {
            "command_key_fieldvalues": "HMSET",
            "key": "foo",
            "field": "bar",
            "value": "hello-world",
        },
    )
    judge_command(
        "HMSET foo bar hello-world key2 value2",
        {
            "command_key_fieldvalues": "HMSET",
            "key": "foo",
            "field": "key2",
            "value": "value2",
        },
    )


def test_hexists(judge_command):
    judge_command(
        "HEXISTS foo bar",
        {"command_key_field": "HEXISTS", "key": "foo", "field": "bar"},
    )
    judge_command("HEXISTS foo bar hello-world", None)
