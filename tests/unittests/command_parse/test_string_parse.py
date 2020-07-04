def test_set(judge_command):
    judge_command("SET abc bar", {"command": "SET", "key": "abc", "value": "bar"})
    judge_command(
        "SET abc bar EX 10",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "EX",
            "millisecond": "10",
        },
    )
    judge_command(
        "SET abc bar px 10000",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px",
            "millisecond": "10000",
        },
    )
    judge_command(
        "SET abc bar px 10000 nx",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px",
            "millisecond": "10000",
            "condition": "nx",
        },
    )
    judge_command(
        "SET abc bar px 10000 XX",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px",
            "millisecond": "10000",
            "condition": "XX",
        },
    )
    judge_command(
        "SET abc bar XX px 10000",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px",
            "millisecond": "10000",
            "condition": "XX",
        },
    )
    judge_command(
        "SET abc bar XX",
        {"command": "SET", "key": "abc", "value": "bar", "condition": "XX"},
    )
    # keepttl
    judge_command(
        "SET abc bar XX keepttl",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "condition": "XX",
            "keepttl": "keepttl",
        },
    )
    judge_command(
        "SET abc bar keepttl XX",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "condition": "XX",
            "keepttl": "keepttl",
        },
    )
    judge_command(
        "SET abc bar XX px 10000 KEEPTTL",
        {
            "command": "SET",
            "key": "abc",
            "value": "bar",
            "expiration": "px",
            "millisecond": "10000",
            "condition": "XX",
            "keepttl": "KEEPTTL",
        },
    )


def test_append(judge_command):
    judge_command("append foo bar", {"command": "append", "key": "foo", "value": "bar"})
    judge_command(
        "APPEND foo 'bar'", {"command": "APPEND", "key": "foo", "value": "'bar'"}
    )
    judge_command("APPEND foo", None)


def test_bitcount(judge_command):
    judge_command("bitcount foo", {"command": "bitcount", "key": "foo"})
    judge_command(
        "bitcount foo 1 5",
        {"command": "bitcount", "key": "foo", "start": "1", "end": "5"},
    )
    judge_command(
        "bitcount foo 1 -5",
        {"command": "bitcount", "key": "foo", "start": "1", "end": "-5"},
    )
    judge_command(
        "bitcount foo -2 -1",
        {"command": "bitcount", "key": "foo", "start": "-2", "end": "-1"},
    )
    judge_command("bitcount foo -2", None)


def test_getrange(judge_command):
    judge_command("getrange foo", None)
    judge_command(
        "getrange foo 1 5",
        {"command": "getrange", "key": "foo", "start": "1", "end": "5"},
    )
    judge_command(
        "getrange foo 1 -5",
        {"command": "getrange", "key": "foo", "start": "1", "end": "-5"},
    )
    judge_command(
        "getrange foo -2 -1",
        {"command": "getrange", "key": "foo", "start": "-2", "end": "-1"},
    )
    judge_command("getrange foo -2", None)


def test_get_set(judge_command):
    judge_command("GETSET abc bar", {"command": "GETSET", "key": "abc", "value": "bar"})


def test_incr(judge_command):
    judge_command("INCR foo", {"command": "INCR", "key": "foo"})
    judge_command("INCR", None)
    judge_command("INCR foo 1", None)


def test_incr_by(judge_command):
    judge_command("INCRBY foo", None)
    judge_command("INCRBY", None)
    judge_command("INCRBY foo 1", {"command": "INCRBY", "key": "foo", "delta": "1"})
    judge_command("INCRBY foo 200", {"command": "INCRBY", "key": "foo", "delta": "200"})
    judge_command("INCRBY foo -21", {"command": "INCRBY", "key": "foo", "delta": "-21"})


def test_decr(judge_command):
    judge_command("DECR foo", {"command": "DECR", "key": "foo"})
    judge_command("DECR", None)
    judge_command("DECR foo 1", None)


def test_decr_by(judge_command):
    judge_command("DECRBY foo", None)
    judge_command("DECRBY", None)
    judge_command("DECRBY foo 1", {"command": "DECRBY", "key": "foo", "delta": "1"})
    judge_command("DECRBY foo 200", {"command": "DECRBY", "key": "foo", "delta": "200"})
    judge_command("DECRBY foo -21", {"command": "DECRBY", "key": "foo", "delta": "-21"})


def test_command_set_range(judge_command):
    judge_command(
        "SETRANGE foo 10 bar",
        {"command": "SETRANGE", "key": "foo", "offset": "10", "value": "bar"},
    )
    judge_command("SETRANGE foo bar", None)
    judge_command(
        "SETRANGE Redis 10 'hello world'",
        {
            "command": "SETRANGE",
            "key": "Redis",
            "offset": "10",
            "value": "'hello world'",
        },
    )


def test_command_set_ex(judge_command):
    judge_command(
        "SETEX key 10 value",
        {"command": "SETEX", "key": "key", "second": "10", "value": "value"},
    )
    judge_command("SETEX foo 10", None)
    judge_command(
        "setex Redis 10 'hello world'",
        {"command": "setex", "key": "Redis", "second": "10", "value": "'hello world'"},
    )


def test_command_setbit(judge_command):
    judge_command(
        "SETBIT key 10 0",
        {"command": "SETBIT", "key": "key", "offset": "10", "bit": "0"},
    )
    judge_command(
        "SETBIT foo 10 1",
        {"command": "SETBIT", "key": "foo", "offset": "10", "bit": "1"},
    )
    judge_command("SETBIT foo 10 10", None)
    judge_command("SETBIT foo 10 abc", None)
    judge_command("SETBIT foo 10", None)
    judge_command("SETBIT foo", None)


def test_command_getbit(judge_command):
    judge_command("GETBIT key 10", {"command": "GETBIT", "key": "key", "offset": "10"})
    judge_command("GETBIT foo 0", {"command": "GETBIT", "key": "foo", "offset": "0"})
    judge_command("GETBIT foo -1", None)
    judge_command("SETBIT foo abc", None)
    judge_command("SETBIT foo", None)


def test_command_incrbyfloat(judge_command):
    judge_command("INCRBYFLOAT key", None)
    judge_command(
        "INCRBYFLOAT key 1.1", {"command": "INCRBYFLOAT", "key": "key", "float": "1.1"}
    )
    judge_command(
        "INCRBYFLOAT key .1", {"command": "INCRBYFLOAT", "key": "key", "float": ".1"}
    )
    judge_command(
        "INCRBYFLOAT key 1.", {"command": "INCRBYFLOAT", "key": "key", "float": "1."}
    )
    judge_command(
        "INCRBYFLOAT key 5.0e3",
        {"command": "INCRBYFLOAT", "key": "key", "float": "5.0e3"},
    )
    judge_command(
        "INCRBYFLOAT key -5.0e3",
        {"command": "INCRBYFLOAT", "key": "key", "float": "-5.0e3"},
    )


def test_command_mget(judge_command):
    judge_command("mget foo bar", {"command": "mget", "keys": "foo bar"})


def test_mset(judge_command):
    judge_command("mset foo bar", {"command": "mset", "key": "foo", "value": "bar"})
    judge_command(
        "mset foo bar hello world",
        {"command": "mset", "key": "hello", "value": "world"},
    )


def test_psetex(judge_command):
    judge_command(
        "psetex foo 1000 bar",
        {"command": "psetex", "key": "foo", "value": "bar", "millisecond": "1000"},
    )
    judge_command("psetex foo bar", None)


def test_bitop(judge_command):
    judge_command(
        "BITOP AND dest key1 key2",
        {"command": "BITOP", "operation": "AND", "key": "dest", "keys": "key1 key2"},
    )
    judge_command(
        "BITOP AND dest key1",
        {"command": "BITOP", "operation": "AND", "key": "dest", "keys": "key1"},
    )
    judge_command("BITOP AND dest", None)


def test_bitpos(judge_command):
    judge_command(
        "BITPOS mykey 1 3 5",
        {"command": "BITPOS", "key": "mykey", "bit": "1", "start": "3", "end": "5"},
    )
    judge_command("BITPOS mykey 1", {"command": "BITPOS", "key": "mykey", "bit": "1"})
    judge_command(
        "BITPOS mykey 1 3",
        {"command": "BITPOS", "key": "mykey", "bit": "1", "start": "3"},
    )


def test_bitfield(judge_command):
    judge_command(
        "BITFIELD mykey INCRBY i5 100 1 GET u4 0",
        {
            "command": "BITFIELD",
            "key": "mykey",
            "incrby": "INCRBY",
            "inttype": ["i5", "u4"],
            "offset": ["100", "0"],
            "value": "1",
            "get": "GET",
        },
    )
    judge_command(
        "BITFIELD mystring SET i8 #0 100",
        {
            "command": "BITFIELD",
            "key": "mystring",
            "set": "SET",
            "inttype": "i8",
            "offset": "#0",
            "value": "100",
        },
    )
    judge_command(
        "BITFIELD mykey incrby u2 100 1 OVERFLOW SAT incrby u2 102 1",
        {
            "command": "BITFIELD",
            "key": "mykey",
            "incrby": "incrby",
            "inttype": "u2",
            "offset": "102",
            "value": "1",
            "overflow": "OVERFLOW",
            "overflow_option": "SAT",
        },
    )


def test_stralgo(judge_command):
    judge_command(
        "STRALGO LCS STRINGS ohmytext mynewtext",
        {
            "command": "STRALGO",
            "str_algo": "LCS",
            "strings_const": "STRINGS",
            "values": "ohmytext mynewtext",
        },
    )

    # Due to redis' command design, this can't be fix in any ways.
    judge_command(
        "STRALGO LCS STRINGS ohmytext mynewtext LEN",
        {
            "command": "STRALGO",
            "str_algo": "LCS",
            "strings_const": "STRINGS",
            "values": "ohmytext mynewtext LEN",
        },
    )
