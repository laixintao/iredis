def test_wrong_select_db_index(cli):
    cli.sendline("select 1")
    cli.expect(["OK", "127.0.0.1"])

    cli.sendline("select 128")
    cli.expect(["DB index is out of range", "127.0.0.1:6379[1]>"])

    cli.sendline("select abc")
    cli.expect(["invalid DB index", "127.0.0.1:6379[1]>"])

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
