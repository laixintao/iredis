def test_restore_command(clean_redis, cli):
    cli.sendline(r'restore foo1 0 "\x00\x03bar\t\x006L\x18\xac\xba\xe0\x9e\xa6"')
    cli.expect(["OK", "127.0.0.1"])

    cli.sendline("get foo1")
    cli.expect('"bar"')
