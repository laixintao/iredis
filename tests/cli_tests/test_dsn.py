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

    # overwrite with -n
    cli = pexpect.spawn("iredis --iredisrc /tmp/iredisrc --dsn local -n 3", timeout=1)
    cli.logfile_read = open("cli_test.log", "ab")
    cli.expect(["iredis", "localhost:6379[3]>"])
    cli.close()

    # dsn not exists
    cli = pexpect.spawn("iredis --iredisrc /tmp/iredisrc --dsn ghost-dsn", timeout=1)
    cli.expect(["Could not find the specified DSN in the config file."])
    cli.close()
    assert cli.status == 1


def test_using_dsn_unix():
    config_content = dedent(
        """
        [alias_dsn]
        unix = unix:///tmp/redis.sock?db=3
        """
    )
    with open("/tmp/iredisrc", "w+") as etc_config:
        etc_config.write(config_content)

    cli = pexpect.spawn("iredis --iredisrc /tmp/iredisrc --dsn unix", timeout=2)
    cli.logfile_read = open("cli_test.log", "ab")
    cli.expect(["iredis", "redis /tmp/redis.sock[3]>"])

    cli.close()
