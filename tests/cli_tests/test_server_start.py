import os
import pexpect


def test_short_help_option(config):
    c = pexpect.spawn("iredis -h", timeout=2)

    c.expect("Show this message and exit.")

    c = pexpect.spawn("iredis -h 127.0.0.1")
    c.expect("127.0.0.1:6379>")

    c.close()


def test_server_version_in_starting():
    c = pexpect.spawn("iredis", timeout=2)
    c.expect("redis-server  5")
    c.close()


def test_connection_using_url(clean_redis):
    c = pexpect.spawn("iredis --url redis://localhost:6379/7", timeout=2)
    c.logfile_read = open("cli_test.log", "ab")
    c.expect(["iredis", "127.0.0.1:6379[7]>"])
    c.sendline("set current-db 7")
    c.expect("OK")
    c.close()


def test_connection_using_url_from_env(clean_redis):
    envs = os.environ
    envs["IREDIS_URL"] = "redis://localhost:6379/7"
    c = pexpect.spawn("iredis", timeout=2, env=envs)
    c.logfile_read = open("cli_test.log", "ab")
    c.expect(["iredis", "127.0.0.1:6379[7]>"])
    c.sendline("set current-db 7")
    c.expect("OK")
    c.close()


def test_connect_via_socket():
    c = pexpect.spawn("iredis -s /tmp/iredis9.sock", timeout=2)
    c.logfile_read = open("cli_test.log", "ab")
    c.expect("redis /tmp/iredis9.sock")
