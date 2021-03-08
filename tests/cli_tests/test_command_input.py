import os
import pytest


def test_wrong_select_db_index(cli):
    cli.sendline("select 1")
    cli.expect(["OK", "127.0.0.1"])

    cli.sendline("select 128")
    cli.expect(["DB index is out of range", "127.0.0.1:6379[1]>"])

    if int(os.environ["REDIS_VERSION"]) > 5:
        text = "value is not an integer or out of range"
    else:
        text = "invalid DB index"

    cli.sendline("select abc")
    cli.expect([text, "127.0.0.1:6379[1]>"])

    cli.sendline("select 15")
    cli.expect("OK")


def test_set_command_with_shash(clean_redis, cli):
    cli.sendline("set a \\hello\\")  # legal redis command
    cli.expect("OK")

    cli.sendline("get a")
    cli.expect(r"hello")


def test_enter_key_binding(clean_redis, cli):
    cli.send("set")
    cli.expect("set")
    cli.send("\033[B")  # down
    cli.sendline()  # enter

    cli.sendline(" a 'hello'")
    cli.expect("OK")

    cli.sendline("get a")
    cli.expect(r"hello")


@pytest.mark.skipif("int(os.environ['REDIS_VERSION']) < 6")
def test_auth_hidden_password_with_username(clean_redis, cli):
    cli.send("auth  default hello-world")
    cli.expect("default")
    cli.expect(r"\*{11}")


@pytest.mark.skipif("int(os.environ['REDIS_VERSION']) > 5")
def test_auth_hidden_password(clean_redis, cli):
    cli.send("auth hello-world")
    cli.expect("auth")
    cli.expect(r"\*{11}")


def test_hello_command_is_not_supported(cli):
    cli.sendline("hello 3")
    cli.expect("IRedis currently not support RESP3")
