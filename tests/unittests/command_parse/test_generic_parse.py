def test_del(judge_command):
    judge_command("DEL abc", {"command": "DEL", "keys": "abc"})
    judge_command("DEL bc1", {"command": "DEL", "keys": "bc1"})
    judge_command("DEL 1", {"command": "DEL", "keys": "1"})
    judge_command('DEL "hello world"', {"command": "DEL", "keys": '"hello world"'})
    judge_command(
        r'DEL "hell\"o world"', {"command": "DEL", "keys": r'"hell\"o world"'}
    )
    judge_command("DEL abc def", {"command": "DEL", "keys": "abc def"})
    judge_command("DEL 1 2", {"command": "DEL", "keys": "1 2"})
    judge_command("DEL 'he \"llo'", {"command": "DEL", "keys": "'he \"llo'"})
    judge_command(
        """DEL 'he "llo' "abc" 'def' """,
        {"command": "DEL", "keys": "'he \"llo' \"abc\" 'def'"},
    )


def test_exists(judge_command):
    judge_command("EXISTS foo bar", {"command": "EXISTS", "keys": "foo bar"})
    judge_command("EXISTS foo", {"command": "EXISTS", "keys": "foo"})
    judge_command("EXISTS 1", {"command": "EXISTS", "keys": "1"})
    judge_command('EXISTS "foo bar"', {"command": "EXISTS", "keys": '"foo bar"'})
    judge_command(r'EXISTS "\""', {"command": "EXISTS", "keys": r'"\""'})


def test_expire(judge_command):
    judge_command("EXPIRE key 12", {"command": "EXPIRE", "key": "key", "second": "12"})
    judge_command("EXPIRE key a12", None)
    judge_command("EXPIRE 12 12", {"command": "EXPIRE", "key": "12", "second": "12"})
    judge_command("EXPIRE 12", None)


def test_expireat(judge_command):
    judge_command(
        "EXPIRE key 1565787643",
        {"command": "EXPIRE", "key": "key", "second": "1565787643"},
    )
    judge_command("EXPIRE key a12", None)


def test_keys(judge_command):
    judge_command("KEYS *", {"command": "KEYS", "pattern": "*"})
    judge_command("KEYS *abc", {"command": "KEYS", "pattern": "*abc"})
    judge_command("keys abc*", {"command": "keys", "pattern": "abc*"})


def test_move(judge_command):
    judge_command("MOVE key 14", {"command": "MOVE", "key": "key", "index": "14"})


def test_pexpire(judge_command):
    judge_command(
        "PEXPIRE key 12", {"command": "PEXPIRE", "key": "key", "millisecond": "12"}
    )
    judge_command("PEXPIRE key a12", None)
    judge_command(
        "PEXPIRE 12 12", {"command": "PEXPIRE", "key": "12", "millisecond": "12"}
    )
    judge_command("PEXPIRE 12", None)


def test_pexpireat(judge_command):
    judge_command(
        "PEXPIREAT key 1565787643",
        {"command": "PEXPIREAT", "key": "key", "timestampms": "1565787643"},
    )
    judge_command("PEXPIREAT key a12", None)


def test_rename(judge_command):
    judge_command(
        "rename key newkey", {"command": "rename", "key": "key", "newkey": "newkey"}
    )
    judge_command(
        "rename 123 newkey", {"command": "rename", "key": "123", "newkey": "newkey"}
    )
    judge_command("rename 123 ", None)


def test_scan(judge_command):
    judge_command(
        "SCAN 0 MATCH task* COUNT 15 TYPE string",
        {
            "command": "SCAN",
            "cursor": "0",
            "match": "MATCH",
            "pattern": "task*",
            "count_const": "COUNT",
            "count": "15",
            "type_const": "TYPE",
            "type": "string",
        },
    )
    judge_command("SCAN 0", {"command": "SCAN", "cursor": "0"})
    judge_command(
        "SCAN 0 MATCH task*",
        {"command": "SCAN", "cursor": "0", "match": "MATCH", "pattern": "task*"},
    )
    judge_command(
        "SCAN 0 COUNT 15 TYPE string",
        {
            "command": "SCAN",
            "cursor": "0",
            "count_const": "COUNT",
            "count": "15",
            "type_const": "TYPE",
            "type": "string",
        },
    )


def test_migrate(judge_command):
    judge_command(
        'MIGRATE 192.168.1.34 6379 " " 0 5000 KEYS key1 key2 key3',
        {
            "command": "MIGRATE",
            "host": "192.168.1.34",
            "port": "6379",
            "key": '" "',
            "index": "0",
            "timeout": "5000",
            "const_keys": "KEYS",
            "keys": "key1 key2 key3",
        },
    )
    judge_command(
        "MIGRATE 192.168.1.34 6379 foo 0 5000 auth password1 KEYS key1 key2 key3",
        {
            "command": "MIGRATE",
            "host": "192.168.1.34",
            "port": "6379",
            "key": "foo",
            "index": "0",
            "timeout": "5000",
            "const_keys": "KEYS",
            "keys": "key1 key2 key3",
            "auth": "auth",
            "password": "password1",
        },
    )
    judge_command(
        "MIGRATE 192.168.1.34 6379 foo 0 5000 auth username1 password1 KEYS key1 key2 key3",
        {
            "command": "MIGRATE",
            "host": "192.168.1.34",
            "port": "6379",
            "key": "foo",
            "index": "0",
            "timeout": "5000",
            "const_keys": "KEYS",
            "keys": "key1 key2 key3",
            "auth": "auth",
            "password": "password1",
            "username": "username1",
        },
    )


def test_object(judge_command):
    judge_command(
        "object refcount mylist",
        {"command": "object", "object": "refcount", "key": "mylist"},
    )


def test_wait(judge_command):
    judge_command("WAIT 3 100", {"command": "WAIT", "count": "3", "timeout": "100"})


def test_restore(judge_command):
    judge_command(
        'RESTORE mykey 0 "\n\x17\x17\x00\x00\x00\x12\x00\x00\x00\x03\x00\x00\xc0\x01\x00\x04\xc0\x02\x00\x04\xc0\x03\x00\xff\x04\x00u#<\xc0;.\xe9\xdd"',  # noqa
        {
            "command": "RESTORE",
            "key": "mykey",
            "timeout": "0",
            "value": '"\n\x17\x17\x00\x00\x00\x12\x00\x00\x00\x03\x00\x00\xc0\x01\x00\x04\xc0\x02\x00\x04\xc0\x03\x00\xff\x04\x00u#<\xc0;.\xe9\xdd"',  # noqa
        },
    )
