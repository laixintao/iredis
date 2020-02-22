def test_integer_type_completer(cli):
    cli.expect("127.0.0.1")
    cli.send("BITFIELD meykey GET ")
    cli.expect(["i64", "u63", "u62"])
    cli.sendline("u4 #0")
    cli.expect("127.0.0.1")

    cli.send("BITFIELD meykey GET ")
    cli.expect(["u4", "i64", "u63", "u62"])


def test_command_completion_when_a_command_is_another_command_substring(
    cli, clean_redis
):
    cli.expect("127.0.0.1")
    cli.send("set")
    cli.expect(["SET", "SETNX", "SETEX", "SETBIT", "SETRANGE"])

    cli.send("n")
    cli.expect("SETNX")
    cli.send("x")
    cli.expect("SETNX")
    cli.sendline("foo bar")
    cli.expect(["1", "127.0.0.1"])

    cli.send("setnx")
    cli.expect("foo")
