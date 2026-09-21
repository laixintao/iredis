import subprocess

import pytest


@pytest.mark.parametrize("stdin", [b"", b"ECHO from-stdin\n"])
def test_command_arguments_with_redirected_stdin(stdin):
    result = subprocess.run(
        ["iredis", "-n", "15", "ECHO", "from-command-line"],
        input=stdin,
        capture_output=True,
        timeout=10,
        check=True,
    )

    assert result.stdout == b"from-command-line\n"


def test_piped_command_without_arguments():
    result = subprocess.run(
        ["iredis", "-n", "15"],
        input=b"PING\n",
        capture_output=True,
        timeout=10,
        check=True,
    )

    assert result.stdout == b"PONG\n"
