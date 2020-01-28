import pytest
import pexpect


def test_trasaction_rprompt(cli):
    cli.sendline("multi")
    cli.expect("OK")
    cli.expect("transaction")

    cli.sendline("get foo")
    cli.expect("QUEUED")

    cli.sendline("EXEC")


def test_trasaction_syntax_error(cli):
    cli.sendline("multi")
    cli.sendline("get foo 1")
    cli.expect("wrong number of arguments for 'get' command")
    cli.expect("transaction")

    cli.sendline("EXEC")
    cli.expect("Transaction discarded because of previous errors.")
    with pytest.raises(pexpect.exceptions.TIMEOUT):
        cli.expect("transaction")
