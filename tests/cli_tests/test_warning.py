from iredis.warning import is_dangerous


def test_is_dangerous():
    assert is_dangerous("KEYS") == (
        True,
        "KEYS will hang redis server, use SCAN instead",
    )


def test_warning_for_dangerous_command(cli):
    cli.sendline("config set save '900 1'")
    cli.expect("Do you want to proceed?")
    cli.sendline("yes")

    cli.sendline("config get save")
    cli.expect("900 1")


def test_warnings_in_raw_mode(clean_redis, raw_cli):
    clean_redis.set("foo", "bar")
    raw_cli.sendline("keys *")
    raw_cli.expect("Do you want to proceed?")
    raw_cli.sendline("y")
    raw_cli.expect("foo")
