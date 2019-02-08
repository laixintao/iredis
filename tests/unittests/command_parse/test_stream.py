def test_xrange(judge_command):
    judge_command(
        "XRANGE somestream - +",
        {"command": "XRANGE", "key": "somestream", "stream_id": ["-", "+"]},
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069",
        {
            "command": "XRANGE",
            "key": "somestream",
            "stream_id": ["1526985054069", "1526985055069"],
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "stream_id": ["1526985054069", "1526985055069-10"],
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10 count 10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "stream_id": ["1526985054069", "1526985055069-10"],
            "count_const": "count",
            "count": "10",
        },
    )


def test_xgroup_create(judge_command):
    judge_command(
        "XGROUP CREATE mykey mygroup 123",
        {
            "command": "XGROUP",
            "stream_create": "CREATE",
            "key": "mykey",
            "group": "mygroup",
            "stream_id": "123",
        },
    )
    judge_command(
        "XGROUP CREATE mykey mygroup $",
        {
            "command": "XGROUP",
            "stream_create": "CREATE",
            "key": "mykey",
            "group": "mygroup",
            "stream_id": "$",
        },
    )
    # short of a parameter
    judge_command("XGROUP CREATE mykey mygroup", None)
    judge_command("XGROUP CREATE mykey", None)


def test_xgroup_setid(judge_command):
    judge_command(
        "XGROUP SETID mykey mygroup 123",
        {
            "command": "XGROUP",
            "stream_setid": "SETID",
            "key": "mykey",
            "group": "mygroup",
            "stream_id": "123",
        },
    )
    judge_command(
        "XGROUP SETID mykey mygroup $",
        {
            "command": "XGROUP",
            "stream_setid": "SETID",
            "key": "mykey",
            "group": "mygroup",
            "stream_id": "$",
        },
    )
    # two subcommand together shouldn't match
    judge_command("XGROUP CREATE mykey mygroup 123 SETID mykey mygroup $", None)


def test_xgroup_destroy(judge_command):
    judge_command(
        "XGROUP destroy mykey mygroup",
        {
            "command": "XGROUP",
            "stream_destroy": "destroy",
            "key": "mykey",
            "group": "mygroup",
        },
    )
    judge_command("XGROUP destroy mykey", None)
    judge_command("XGROUP DESTROY mykey mygroup $", None)


def test_xgroup_delconsumer(judge_command):
    judge_command(
        "XGROUP delconsumer mykey mygroup myconsumer",
        {
            "command": "XGROUP",
            "stream_delconsumer": "delconsumer",
            "key": "mykey",
            "group": "mygroup",
            "consumer": "myconsumer",
        },
    )
    judge_command(
        "XGROUP delconsumer mykey mygroup $",
        {
            "command": "XGROUP",
            "stream_delconsumer": "delconsumer",
            "key": "mykey",
            "group": "mygroup",
            "consumer": "$",
        },
    )
    judge_command("XGROUP delconsumer mykey mygroup", None)


def test_xgroup_stream(judge_command):
    judge_command(
        "XACK mystream group1 123123",
        {
            "command": "XACK",
            "key": "mystream",
            "group": "group1",
            "stream_id": "123123",
        },
    )
    judge_command(
        "XACK mystream group1 123123 111",
        {"command": "XACK", "key": "mystream", "group": "group1", "stream_id": "111"},
    )
