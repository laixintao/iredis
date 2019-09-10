def test_zcount(judge_command):
    judge_command(
        "zcount foo -10 0",
        {"command_key_min_max": "zcount", "key": "foo", "min": "-10", "max": "0"},
    )


def test_bzpopmax(judge_command):
    judge_command(
        "bzpopmax set set2 set3 4",
        {"command_keys_timeout": "bzpopmax", "keys": "set set2 set3", "timeout": "4"},
    )
    judge_command(
        "bzpopmin set   4",
        {"command_keys_timeout": "bzpopmin", "keys": "set", "timeout": "4"},
    )
