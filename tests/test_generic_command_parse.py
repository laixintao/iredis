def test_del(judge_command):
    judge_command("DEL abc", {"command_keys": "DEL", "keys": "abc"})
    judge_command("DEL bc1", {"command_keys": "DEL", "keys": "bc1"})
    judge_command("DEL 1", {"command_keys": "DEL", "keys": "1"})
    judge_command('DEL "hello world"', {"command_keys": "DEL", "keys": '"hello world"'})
    judge_command(
        r'DEL "hell\"o world"', {"command_keys": "DEL", "keys": r'"hell\"o world"'}
    )
    judge_command("DEL abc def", {"command_keys": "DEL", "keys": "abc def"})
    judge_command("DEL 1 2", {"command_keys": "DEL", "keys": "1 2"})
    judge_command("DEL 'he \"llo'", {"command_keys": "DEL", "keys": "'he \"llo'"})
    judge_command("""DEL 'he "llo' "abc" 'def' """, {"command_keys": "DEL", "keys": "'he \"llo' \"abc\" 'def'"})


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


def test_pexpire(judge_command):
    judge_command(
        "PEXPIRE key 12",
        {"command_key_millisecond": "PEXPIRE", "key": "key", "millisecond": "12"},
    )
    judge_command("PEXPIRE key a12", None)
    judge_command(
        "PEXPIRE 12 12",
        {"command_key_millisecond": "PEXPIRE", "key": "12", "millisecond": "12"},
    )
    judge_command("PEXPIRE 12", None)


def test_pexpireat(judge_command):
    judge_command(
        "PEXPIREAT key 1565787643",
        {
            "command_key_timestampms": "PEXPIREAT",
            "key": "key",
            "timestampms": "1565787643",
        },
    )
    judge_command("PEXPIREAT key a12", None)


def test_rename(judge_command):
    judge_command(
        "rename key newkey",
        {"command_key_newkey": "rename", "key": "key", "newkey": "newkey"},
    )
    judge_command(
        "rename 123 newkey",
        {"command_key_newkey": "rename", "key": "123", "newkey": "newkey"},
    )
    judge_command("rename 123 ", None)
