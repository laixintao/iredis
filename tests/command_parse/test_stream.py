def test_xrange(judge_command):
    judge_command(
        "XRANGE somestream - +",
        {"command": "XRANGE", "key": "somestream", "sstart": "-", "send": "+"},
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069",
        {
            "command": "XRANGE",
            "key": "somestream",
            "sstart": "1526985054069",
            "send": "1526985055069",
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "sstart": "1526985054069",
            "send": "1526985055069-10",
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10 count 10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "sstart": "1526985054069",
            "send": "1526985055069-10",
            "count_const": "count",
            "count": "10",
        },
    )
