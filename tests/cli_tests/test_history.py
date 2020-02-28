import os


def test_history_not_log_auth(cli):
    cli.sendline("AUTH 123")
    cli.expect(["Client sent AUTH, but no password is set", "127.0.0.1"])
    cli.sendline("set foo bar")
    cli.expect("OK")

    with open(os.path.expanduser("~/.iredis_history"), "r") as history_file:
        content = history_file.read()

    assert "set foo bar" in content
    assert "AUTH" not in content
