def test_integer_type_completer(cli):
    cli.expect("127.0.0.1")
    cli.send("BITFIELD meykey GET ")
    cli.expect(["i64", "u63", "u62"])
    cli.sendline("u4 #0")
    cli.expect("127.0.0.1")

    cli.send("BITFIELD meykey GET ")
    cli.expect(["u4", "i64", "u63", "u62"])
