def test_del(judge_command):
    judge_command("DEL abc", {"command_key": "DEL", "key": "abc"})
    judge_command("DEL bc1", {"command_key": "DEL", "key": "bc1"})
    judge_command("DEL 1", {"command_key": "DEL", "key": "1"})
    judge_command("DEL 1 2", None)
    judge_command('DEL "hello world"', {"command_key": "DEL", "key": '"hello world"'})
    judge_command(
        r'DEL "hell\"o world"', {"command_key": "DEL", "key": r'"hell\"o world"'}
    )


def test_exists(judge_command):
    judge_command("EXISTS foo bar", {"command_keys": "EXISTS", "keys": "foo bar"})
    judge_command("EXISTS foo", {"command_keys": "EXISTS", "keys": "foo"})
    judge_command("EXISTS 1", {"command_keys": "EXISTS", "keys": "1"})
    judge_command('EXISTS "foo bar"', {"command_keys": "EXISTS", "keys": '"foo bar"'})
    judge_command(r'EXISTS "\""', {"command_keys": "EXISTS", "keys": r'"\""'})


def test_expire(judge_command):
    judge_command(
        "EXPIRE key 12", {"command_key_second": "EXPIRE", "key": "key", "second": "12"}
    )
    judge_command("EXPIRE key a12", None)
    judge_command(
        "EXPIRE 12 12", {"command_key_second": "EXPIRE", "key": "12", "second": "12"}
    )
    judge_command("EXPIRE 12", None)


def test_expireat(judge_command):
    judge_command(
        "EXPIRE key 1565787643",
        {"command_key_second": "EXPIRE", "key": "key", "second": "1565787643"},
    )
    judge_command("EXPIRE key a12", None)


def test_keys(judge_command):
    judge_command("KEYS *", {"command_pattern": "KEYS", "pattern": "*"})
    judge_command("KEYS *abc", {"command_pattern": "KEYS", "pattern": "*abc"})
    judge_command("keys abc*", {"command_pattern": "keys", "pattern": "abc*"})


def test_move(judge_command):
    judge_command(
        "MOVE key 14", {"command_key_index": "MOVE", "key": "key", "index": "14"}
    )

