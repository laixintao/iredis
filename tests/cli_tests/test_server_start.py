import pexpect


def test_short_help_option(config):
    c = pexpect.spawn("iredis -h", timeout=0.5)

    c.expect("Show this message and exit.")

    c = pexpect.spawn("iredis -h 127.0.0.1")
    c.expect("127.0.0.1:6379>")

    c.close()


def test_server_version_in_starting():
    c = pexpect.spawn("iredis", timeout=0.5)
    c.expect("redis-server  5")
    c.close()
