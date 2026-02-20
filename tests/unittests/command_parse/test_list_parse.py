def test_lpop_rpop(judge_command):
    """LPOP/RPOP accept key and optional count (per commands.json since 6.2)."""
    judge_command("LPOP mylist", {"command": "LPOP", "key": "mylist"})
    judge_command(
        "LPOP mylist 3",
        {"command": "LPOP", "key": "mylist", "count": "3"},
    )
    judge_command("RPOP mylist", {"command": "RPOP", "key": "mylist"})
    judge_command(
        "RPOP mylist 2",
        {"command": "RPOP", "key": "mylist", "count": "2"},
    )


def test_rpushx(judge_command):
    """RPUSHX accepts key and one or more elements (per commands.json since 4.0)."""
    judge_command(
        "RPUSHX mylist a",
        {"command": "RPUSHX", "key": "mylist", "values": "a"},
    )
    judge_command(
        "RPUSHX mylist a b c",
        {"command": "RPUSHX", "key": "mylist", "values": "a b c"},
    )


def test_rpush(judge_command):
    judge_command(
        "RPUSH list1 foo bar hello world",
        {"command": "RPUSH", "key": "list1", "values": "foo bar hello world"},
    )
    judge_command(
        "LPUSH list1 foo", {"command": "LPUSH", "key": "list1", "values": "foo"}
    )


def test_lindex(judge_command):
    judge_command(
        "LINDEX list1 10", {"command": "LINDEX", "key": "list1", "position": "10"}
    )
    judge_command(
        "LINDEX list1 -10", {"command": "LINDEX", "key": "list1", "position": "-10"}
    )
    judge_command("LINDEX list1 1.1", None)


def test_lset(judge_command):
    judge_command(
        "LSET list1 10 newbie",
        {"command": "LSET", "key": "list1", "position": "10", "value": "newbie"},
    )
    judge_command(
        "LSET list1 -1 newbie",
        {"command": "LSET", "key": "list1", "position": "-1", "value": "newbie"},
    )


def test_brpoplpush(judge_command):
    judge_command(
        "BRPOPLPUSH list1 list2 10",
        {"command": "BRPOPLPUSH", "key": "list1", "newkey": "list2", "timeout": "10"},
    )
    judge_command(
        "BRPOPLPUSH list1 list2 0",
        {"command": "BRPOPLPUSH", "key": "list1", "newkey": "list2", "timeout": "0"},
    )
    judge_command("BRPOPLPUSH list1 list2 -1", None)


def test_brpoplpush_with_double_timeout(judge_command):
    judge_command(
        "BRPOPLPUSH list1 list2 10.0",
        {"command": "BRPOPLPUSH", "key": "list1", "newkey": "list2", "timeout": "10.0"},
    )
    judge_command(
        "BRPOPLPUSH list1 list2 .2",
        {"command": "BRPOPLPUSH", "key": "list1", "newkey": "list2", "timeout": ".2"},
    )
    judge_command("BRPOPLPUSH list1 list2 12.", None)


def test_linsert(judge_command):
    judge_command(
        'LINSERT mylist BEFORE "World" "There"',
        {
            "command": "LINSERT",
            "key": "mylist",
            "position_choice": "BEFORE",
            "value": ['"World"', '"There"'],
        },
    )
    judge_command(
        'LINSERT mylist after "World" "There"',
        {
            "command": "LINSERT",
            "key": "mylist",
            "position_choice": "after",
            "value": ['"World"', '"There"'],
        },
    )


def test_lpos(judge_command):
    judge_command("LPOS mylist c", {"command": "LPOS", "key": "mylist", "element": "c"})
    judge_command(
        "LPOS mylist c RANK 2",
        {
            "command": "LPOS",
            "key": "mylist",
            "element": "c",
            "rank_const": "RANK",
            "rank": "2",
        },
    )
    judge_command(
        "LPOS mylist c RANK -1",
        {
            "command": "LPOS",
            "key": "mylist",
            "element": "c",
            "rank_const": "RANK",
            "rank": "-1",
        },
    )
    judge_command(
        "LPOS mylist c COUNT 2",
        {
            "command": "LPOS",
            "key": "mylist",
            "element": "c",
            "count_const": "COUNT",
            "count": "2",
        },
    )
    judge_command(
        "LPOS mylist c RANK -1 COUNT 2",
        {
            "command": "LPOS",
            "key": "mylist",
            "element": "c",
            "count_const": "COUNT",
            "count": "2",
            "rank_const": "RANK",
            "rank": "-1",
        },
    )


def test_blmove(judge_command):
    judge_command(
        "blmove list1 list2 left right 1.2",
        {
            "command": "blmove",
            "key": ["list1", "list2"],
            "lr_const": ["left", "right"],
            "timeout": "1.2",
        },
    )
    judge_command(
        "blmove list1 list2 right right .2",
        {
            "command": "blmove",
            "key": ["list1", "list2"],
            "lr_const": ["right", "right"],
            "timeout": ".2",
        },
    )
    judge_command("blmove list1 list2 right right", None)
    judge_command("blmove list1 right right 1", None)
