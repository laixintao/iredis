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


def test_warnings_in_raw_mode_canceled(clean_redis, raw_cli):
    clean_redis.set("foo", "bar")
    raw_cli.sendline("keys *")
    raw_cli.expect("Do you want to proceed?")
    raw_cli.sendline("n")
    # the f should never appeared
    raw_cli.expect("Canceled![^f]+127.0.0.1")


def test_warnings_confirmed(clean_redis, cli):
    clean_redis.set("foo", "bar")
    cli.sendline("keys *")
    cli.expect("Do you want to proceed?")
    cli.sendline("y")
    cli.expect("foo")


def test_warnings_canceled(clean_redis, cli):
    clean_redis.set("foo", "bar")
    cli.sendline("keys *")
    cli.expect("Do you want to proceed?")
    cli.sendline("n")
    # the f should never appeared
    cli.expect("Canceled![^f]+127.0.0.1")
