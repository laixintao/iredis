from iredis.warning import is_dangerous


def test_is_dangerous():
    assert is_dangerous("KEYS") == (
        True,
        "KEYS will hang redis server, use SCAN instead",
    )


def test_warning_for_dangerous_command(cli, config):
    config.warning = True
    cli.sendline("config set save '900 1'")
    cli.expect("Do you want to proceed?")
    cli.sendline("yes")

    cli.sendline("config get save")
    cli.expect("900 1")
