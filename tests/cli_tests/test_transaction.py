import pytest
import pexpect


def test_trasaction_rprompt(clean_redis, cli):
    cli.sendline("multi")
    cli.expect(["OK", "transaction", "127.0.0.1"])

    cli.sendline("get foo")
    cli.expect(["QUEUED", "127.0.0.1", "transaction"])

    cli.sendline("set hello world")
    cli.expect(["QUEUED", "127.0.0.1", "transaction"])

    cli.sendline("ping")
    cli.expect(["QUEUED", "127.0.0.1", "transaction"])

    cli.sendline("EXEC")
    cli.expect("(nil)")
    cli.expect("OK")
    cli.expect("PONG")
    cli.expect("127.0.0.1")

    with pytest.raises(pexpect.exceptions.TIMEOUT):
        cli.expect("transaction")


def test_trasaction_syntax_error(cli):
    cli.sendline("multi")
    cli.sendline("get foo 1")
    cli.expect(["wrong number of arguments for 'get' command", "transaction"])

    cli.sendline("EXEC")
    cli.expect("Transaction discarded because of previous errors.")
    with pytest.raises(pexpect.exceptions.TIMEOUT):
        cli.expect("transaction")


def test_trasaction_in_raw_mode(clean_redis, raw_cli):
    clean_redis.set("foo", "bar")

    raw_cli.sendline("multi")
    raw_cli.expect(["OK", "transaction", "127.0.0.1"])

    raw_cli.sendline("get foo")
    raw_cli.expect(["QUEUED", "127.0.0.1", "transaction"])

    raw_cli.sendline("EXEC")
    raw_cli.expect("bar")
    raw_cli.expect("127.0.0.1")

    with pytest.raises(pexpect.exceptions.TIMEOUT):
        raw_cli.expect("transaction")


def test_exec_return_nil_when_using_watch(clean_redis, cli):
    cli.sendline("watch foo")
    cli.expect("OK")

    cli.sendline("multi")
    cli.expect("OK")

    cli.sendline("get bar")
    cli.expect("QUEUED")

    # transaction will fail, return nil
    clean_redis.set("foo", "hello!")

    cli.sendline("exec")
    cli.expect("(nil)")
