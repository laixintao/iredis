def test_xrange(judge_command):
    judge_command(
        "XRANGE somestream - +",
        {"command": "XRANGE", "key": "somestream", "s_start_id": "-", "s_end_id": "+"},
    )
    # $ is not a valide id for XRANGE
    judge_command("XRANGE somestream $ +", None)
    judge_command("XRANGE somestream - $", None)
    judge_command("XRANGE somestream + 100", None)
    judge_command("XRANGE somestream 100 -", None)
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069",
        {
            "command": "XRANGE",
            "key": "somestream",
            "s_start_id": "1526985054069",
            "s_end_id": "1526985055069",
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "s_start_id": "1526985054069",
            "s_end_id": "1526985055069-10",
        },
    )
    judge_command(
        "XRANGE somestream  1526985054069 1526985055069-10 count 10",
        {
            "command": "XRANGE",
            "key": "somestream",
            "s_start_id": "1526985054069",
            "s_end_id": "1526985055069-10",
            "count_const": "count",
            "count": "10",
        },
    )