def test_set(cli):
    cli.sendline("set foo bar")
    cli.expect("OK")

    cli.sendline("set foo bar nx")
    cli.expect("(nil)")

    cli.sendline("set foo bar xx")
    cli.expect("OK")

    cli.sendline("set foo1 bar xx")
    cli.expect("(nil)")


def test_get(cli):
    cli.sendline("set foo bar")
    cli.expect("OK")

    cli.sendline("get foo")
    cli.expect('"bar"')


def test_delete_string(clean_redis, cli):
    cli.sendline("set foo bar")
    cli.expect("OK")
    cli.sendline("del foo")
    cli.expect("Do you want to proceed")
    cli.sendline("yes")
    cli.expect("1")

    cli.sendline("get foo")
    cli.expect("(nil)")


def test_on_dangerous_commands(cli):
    cli.sendline("keys *")
    cli.expect("KEYS will hang redis server, use SCAN instead")
