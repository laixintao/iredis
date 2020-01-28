def test_wrong_select_db_index(cli):
    cli.sendline("select 1")
    cli.expect("OK")

    cli.sendline("select 128")
    cli.expect("DB index is out of range")

    cli.sendline("select abc")
    cli.expect("invalid DB index")

    cli.sendline("select 15")
    cli.expect("OK")


def test_set_command_with_shash(clean_redis, cli):
    cli.sendline("set a \\hello\\")  # legal redis command
    cli.expect("OK")

    cli.sendline("get a")
    cli.expect(r"hello")
