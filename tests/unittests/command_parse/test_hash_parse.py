def test_hdel(judge_command):
    judge_command("HDEL foo bar", {"command": "HDEL", "key": "foo", "fields": "bar"})
    judge_command(
        "HDEL foo bar hello world",
        {"command": "HDEL", "key": "foo", "fields": "bar hello world"},
    )


def test_hmset(judge_command):
    judge_command(
        "HMSET foo bar hello-world",
        {"command": "HMSET", "key": "foo", "field": "bar", "value": "hello-world"},
    )
    judge_command(
        "HMSET foo bar hello-world key2 value2",
        {"command": "HMSET", "key": "foo", "field": "key2", "value": "value2"},
    )


def test_hexists(judge_command):
    judge_command(
        "HEXISTS foo bar", {"command": "HEXISTS", "key": "foo", "field": "bar"}
    )
    judge_command("HEXISTS foo bar hello-world", None)


def test_hincrby(judge_command):
    judge_command(
        "HINCRBY foo bar 12",
        {"command": "HINCRBY", "key": "foo", "field": "bar", "delta": "12"},
    )


def test_hincrbyfloat(judge_command):
    judge_command(
        "HINCRBYFLOAT foo bar 12.1",
        {"command": "HINCRBYFLOAT", "key": "foo", "field": "bar", "float": "12.1"},
    )


def test_hset(judge_command):
    judge_command(
        "HSET foo bar hello",
        {"command": "HSET", "key": "foo", "field": "bar", "value": "hello"},
    )
