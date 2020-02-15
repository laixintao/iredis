import pexpect
from textwrap import dedent
from pathlib import Path


def test_log_location_config():
    config_content = dedent(
        """
        [main]
        log_location = /tmp/iredis1.log
        """
    )
    with open("/tmp/iredisrc", "w+") as etc_config:
        etc_config.write(config_content)

    cli = pexpect.spawn("iredis -n 15 --iredisrc /tmp/iredisrc", timeout=1)
    cli.expect("127.0.0.1")
    cli.close()

    log = Path("/tmp/iredis1.log")
    assert log.exists()
    with open(log, "r") as logfile:
        content = logfile.read()

    assert len(content) > 100
