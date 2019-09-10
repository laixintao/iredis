def test_zcount(judge_command):
    judge_command(
        "zcount foo -10 0",
        {"command_key_min_max": "zcount", "key": "foo", "min": "-10", "max": "0"},
    )
