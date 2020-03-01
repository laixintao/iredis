import pexpect
from textwrap import dedent


def test_using_dsn():
    config_content = dedent(
        """
        [alias_dsn]
        local = redis://localhost:6379/15
        """
    )
    with open("/tmp/iredisrc", "w+") as etc_config:
        etc_config.write(config_content)

    cli = pexpect.spawn("iredis --iredisrc /tmp/iredisrc --dsn local", timeout=1)
    cli.logfile_read = open("cli_test.log", "ab")
    cli.expect(["iredis", "localhost:6379[15]>"])
    cli.close()
