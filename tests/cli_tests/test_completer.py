import pytest


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
    cli.expect(["set", "setnx", "setex", "setbit", "setrange"])

    cli.send("n")
    cli.expect("setnx")
    cli.send("x")
    cli.expect("setnx")
    cli.sendline("foo bar")
    cli.expect(["1", "127.0.0.1"])

    cli.send("setnx")
    cli.expect("foo")


def test_command_completion_when_space_command(cli, clean_redis):
    cli.expect("127.0.0.1")

    cli.send("command in")
    cli.expect("command info")


@pytest.mark.skipif("int(os.environ['REDIS_VERSION']) < 6")
def test_username_completer(cli, iredis_client):
    iredis_client.execute("acl setuser", "foo1")
    iredis_client.execute("acl setuser", "bar2")

    cli.expect("127.0.0.1")
    cli.sendline("acl users")
    cli.expect("foo1")

    cli.send("acl deluser ")
    cli.expect("foo1")
    cli.expect("bar2")
