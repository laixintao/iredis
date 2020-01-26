from iredis.warning import is_dangerous


def test_is_dangerous():
    assert is_dangerous("KEYS") == (
        True,
        "KEYS will hang redis server, use SCAN instead",
    )


def test_warning_for_dangerous_command(local_process):
    local_process.sendline("config set save '900 1'")
    local_process.expect("Do you want to proceed?")
    local_process.sendline("yes")

    local_process.sendline("config get save")
    local_process.expect("900 1")
