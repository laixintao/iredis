import pytest


def test_zcount(judge_command):
    judge_command(
        "zcount foo -10 0",
        {"command": "zcount", "key": "foo", "min": "-10", "max": "0"},
    )


def test_bzpopmax(judge_command):
    judge_command(
        "bzpopmax set set2 set3 4",
        {"command": "bzpopmax", "keys": "set set2 set3", "timeout": "4"},
    )
    judge_command(
        "bzpopmin set   4", {"command": "bzpopmin", "keys": "set", "timeout": "4"}
    )


def test_zadd(judge_command):
    judge_command(
        "zadd t 100 qewqr 23 pp 11 oo",
        {
            "command": "zadd",
            "key": "t",
            "score": "11",  # FIXME: only have last one
            "member": "oo",
        },
    )
    judge_command(
        "zadd t incr 100 foo",
        {
            "command": "zadd",
            "key": "t",
            "incr": "incr",
            "score": "100",  # FIXME: only have last one
            "member": "foo",
        },
    )
    judge_command(
        "zadd t NX CH incr 100 foo",
        {
            "command": "zadd",
            "key": "t",
            "condition": "NX",
            "changed": "CH",
            "incr": "incr",
            "score": "100",  # FIXME: only have last one
            "member": "foo",
        },
    )


def test_zincrby(judge_command):
    judge_command(
        "zincrby t 10 foo",
        {"command": "zincrby", "key": "t", "float": "10", "member": "foo"},
    )
    judge_command(
        "zincrby t 2.3 foo",
        {"command": "zincrby", "key": "t", "float": "2.3", "member": "foo"},
    )


def test_zlexcount(judge_command):
    judge_command(
        "zlexcount a - +",
        {"command": "zlexcount", "key": "a", "lexmin": "-", "lexmax": "+"},
    )
    judge_command(
        "zlexcount a (aaaa [z",
        {"command": "zlexcount", "key": "a", "lexmin": "(aaaa", "lexmax": "[z"},
    )
    judge_command(
        "ZLEXCOUNT myset - [c",
        {"command": "ZLEXCOUNT", "key": "myset", "lexmin": "-", "lexmax": "[c"},
    )
    judge_command(
        "ZLEXCOUNT myset [aaa (g",
        {"command": "ZLEXCOUNT", "key": "myset", "lexmin": "[aaa", "lexmax": "(g"},
    )


def test_zrange(judge_command):
    judge_command(
        "zrange foo -1 10",
        {"command": "zrange", "key": "foo", "start": "-1", "end": "10"},
    )
    judge_command(
        "zrange foo 0 -1",
        {"command": "zrange", "key": "foo", "start": "0", "end": "-1"},
    )
    judge_command(
        "zrange foo 0 -1 withscores",
        {
            "command": "zrange",
            "key": "foo",
            "start": "0",
            "end": "-1",
            "withscores": "withscores",
        },
    )


@pytest.mark.xfail(reason="Not implemented yet")
def test_zinterstore(judge_command):
    judge_command("ZINTERSTORE out 2 zset1 zset2 WEIGHTS 2 3", {})
    judge_command("ZINTERSTORE out 2 zset1 zset2 WEIGHTS -1 -2", {})
    judge_command("ZINTERSTORE out 2 zset1 zset2 WEIGHTS 0.2 0.3", {})


def test_zrangebylex(judge_command):
    judge_command(
        "ZRANGEBYLEX myzset [aaa (g",
        {"command": "ZRANGEBYLEX", "key": "myzset", "lexmin": "[aaa", "lexmax": "(g"},
    )
    judge_command(
        "ZRANGEBYLEX myzset - (c",
        {"command": "ZRANGEBYLEX", "key": "myzset", "lexmin": "-", "lexmax": "(c"},
    )
    judge_command(
        "ZRANGEBYLEX myzset - (c limit 10 100",
        {
            "command": "ZRANGEBYLEX",
            "key": "myzset",
            "lexmin": "-",
            "lexmax": "(c",
            "limit": "limit",
            "offset": "10",
            "count": "100",
        },
    )
    judge_command(
        "ZRANGEBYLEX myzset - (c limit 10 -1",
        {
            "command": "ZRANGEBYLEX",
            "key": "myzset",
            "lexmin": "-",
            "lexmax": "(c",
            "limit": "limit",
            "offset": "10",
            "count": "-1",
        },
    )


def test_zrangebyscore(judge_command):
    judge_command(
        "ZRANGEBYSCORE myzset -inf +inf",
        {"command": "ZRANGEBYSCORE", "key": "myzset", "min": "-inf", "max": "+inf"},
    )
    judge_command(
        "ZRANGEBYSCORE myzset 1 2",
        {"command": "ZRANGEBYSCORE", "key": "myzset", "min": "1", "max": "2"},
    )
    judge_command(
        "ZRANGEBYSCORE myzset (1 (2",
        {"command": "ZRANGEBYSCORE", "key": "myzset", "min": "(1", "max": "(2"},
    )
    judge_command(
        "ZRANGEBYSCORE myzset -inf +inf LIMIT 10 100",
        {
            "command": "ZRANGEBYSCORE",
            "key": "myzset",
            "min": "-inf",
            "max": "+inf",
            "limit": "LIMIT",
            "offset": "10",
            "count": "100",
        },
    )
