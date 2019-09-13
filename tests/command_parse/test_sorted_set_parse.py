import pytest


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


def test_zadd(judge_command):
    judge_command(
        "zadd t 100 qewqr 23 pp 11 oo",
        {
            "command_key_condition_changed_incr_score_members": "zadd",
            "key": "t",
            "score": "11",  # FIXME: only have last one
            "member": "oo",
        },
    )
    judge_command(
        "zadd t incr 100 foo",
        {
            "command_key_condition_changed_incr_score_members": "zadd",
            "key": "t",
            "incr": "incr",
            "score": "100",  # FIXME: only have last one
            "member": "foo",
        },
    )
    judge_command(
        "zadd t NX CH incr 100 foo",
        {
            "command_key_condition_changed_incr_score_members": "zadd",
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
        {
            "command_key_float_member": "zincrby",
            "key": "t",
            "float": "10",
            "member": "foo",
        },
    )
    judge_command(
        "zincrby t 2.3 foo",
        {
            "command_key_float_member": "zincrby",
            "key": "t",
            "float": "2.3",
            "member": "foo",
        },
    )


def test_zlexcount(judge_command):
    judge_command(
        "zlexcount a - +",
        {
            "command_key_lexmin_lexmax": "zlexcount",
            "key": "a",
            "lexmin": "-",
            "lexmax": "+",
        },
    )
    judge_command(
        "zlexcount a (aaaa [z",
        {
            "command_key_lexmin_lexmax": "zlexcount",
            "key": "a",
            "lexmin": "(aaaa",
            "lexmax": "[z",
        },
    )
    judge_command(
        "ZLEXCOUNT myset - [c",
        {
            "command_key_lexmin_lexmax": "ZLEXCOUNT",
            "key": "myset",
            "lexmin": "-",
            "lexmax": "[c",
        },
    )
    judge_command(
        "ZLEXCOUNT myset [aaa (g",
        {
            "command_key_lexmin_lexmax": "ZLEXCOUNT",
            "key": "myset",
            "lexmin": "[aaa",
            "lexmax": "(g",
        },
    )


def test_zrange(judge_command):
    judge_command(
        "zrange foo -1 10",
        {
            "command_key_start_end_withscores_x": "zrange",
            "key": "foo",
            "start": "-1",
            "end": "10",
        },
    )
    judge_command(
        "zrange foo 0 -1",
        {
            "command_key_start_end_withscores_x": "zrange",
            "key": "foo",
            "start": "0",
            "end": "-1",
        },
    )
    judge_command(
        "zrange foo 0 -1 withscores",
        {
            "command_key_start_end_withscores_x": "zrange",
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
        {
            "command_key_lexmin_lexmax_limit_offset_count": "ZRANGEBYLEX",
            "key": "myzset",
            "lexmin": "[aaa",
            "lexmax": "(g",
        },
    )
    judge_command(
        "ZRANGEBYLEX myzset - (c",
        {
            "command_key_lexmin_lexmax_limit_offset_count": "ZRANGEBYLEX",
            "key": "myzset",
            "lexmin": "-",
            "lexmax": "(c",
        },
    )
    judge_command(
        "ZRANGEBYLEX myzset - (c limit 10 100",
        {
            "command_key_lexmin_lexmax_limit_offset_count": "ZRANGEBYLEX",
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
            "command_key_lexmin_lexmax_limit_offset_count": "ZRANGEBYLEX",
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
        {
            "command_key_min_max_withscore_x_limit_offset_count_x": "ZRANGEBYSCORE",
            "key": "myzset",
            "min": "-inf",
            "max": "+inf",
        },
    )
    judge_command(
        "ZRANGEBYSCORE myzset 1 2",
        {
            "command_key_min_max_withscore_x_limit_offset_count_x": "ZRANGEBYSCORE",
            "key": "myzset",
            "min": "1",
            "max": "2",
        },
    )
    judge_command(
        "ZRANGEBYSCORE myzset (1 (2",
        {
            "command_key_min_max_withscore_x_limit_offset_count_x": "ZRANGEBYSCORE",
            "key": "myzset",
            "min": "(1",
            "max": "(2",
        },
    )
    judge_command(
        "ZRANGEBYSCORE myzset -inf +inf LIMIT 10 100",
        {
            "command_key_min_max_withscore_x_limit_offset_count_x": "ZRANGEBYSCORE",
            "key": "myzset",
            "min": "-inf",
            "max": "+inf",
            "limit": "LIMIT",
            "offset": "10",
            "count": "100",
        },
    )
