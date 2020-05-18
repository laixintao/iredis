# noqa: F541
import os
import sys
import pexpect
import pathlib
from contextlib import contextmanager
from textwrap import dedent


TEST_IREDISRC = "/tmp/.iredisrc.test"
TEST_PAGER_BOUNDARY = "---boundary---"
TEST_PAGER_BOUNDARY_NUMBER = "---88938347271---"

env_pager = "{0} {1} {2}".format(
    sys.executable,
    os.path.join(pathlib.Path(__file__).parent, "wrappager.py"),
    TEST_PAGER_BOUNDARY,
)
env_pager_numbers = "{0} {1} {2}".format(
    sys.executable,
    os.path.join(pathlib.Path(__file__).parent, "wrappager.py"),
    TEST_PAGER_BOUNDARY_NUMBER,
)


@contextmanager
def pager_enabled_cli():
    env = os.environ
    env["PAGER"] = env_pager
    child = pexpect.spawn("iredis -n 15", timeout=3, env=env)
    child.logfile_read = open("cli_test.log", "ab")
    child.expect("127.0.0.1")
    try:
        yield child
    finally:
        child.close()


def test_using_pager_when_rows_too_high(clean_redis):
    for index in range(100):
        clean_redis.lpush("long-list", f"value-{index}")
    with pager_enabled_cli() as child:
        child.sendline("lrange long-list 0 -1")
        child.expect(TEST_PAGER_BOUNDARY)
        child.expect("value-1")
        child.expect(TEST_PAGER_BOUNDARY)


def test_using_pager_works_for_help():
    with pager_enabled_cli() as child:
        child.sendline("help set")
        child.expect(TEST_PAGER_BOUNDARY)
        child.expect("Set the string value of a key")
        child.expect(TEST_PAGER_BOUNDARY)


def test_pager_works_for_peek(clean_redis):
    for index in range(100):
        clean_redis.lpush("long-list", f"value-{index}")
    with pager_enabled_cli() as child:
        child.sendline("peek long-list")
        child.expect(TEST_PAGER_BOUNDARY)
        child.expect("(quicklist)")
        child.expect("value-1")
        child.expect(TEST_PAGER_BOUNDARY)


def test_using_pager_from_config(clean_redis):
    config_content = dedent(
        f"""
        [main]
        log_location = /tmp/iredis1.log
        pager = {env_pager_numbers}
        """
    )

    with open(TEST_IREDISRC, "w+") as test_iredisrc:
        test_iredisrc.write(config_content)

    child = pexpect.spawn(f"iredis -n 15 --iredisrc {TEST_IREDISRC}", timeout=3)
    child.logfile_read = open("cli_test.log", "ab")
    child.expect("127.0.0.1")
    for index in range(100):
        clean_redis.lpush("long-list", f"value-{index}")
    child.sendline("lrange long-list 0 -1")
    child.expect(TEST_PAGER_BOUNDARY_NUMBER)
    child.expect("value-1")
    child.expect(TEST_PAGER_BOUNDARY_NUMBER)
    child.close()


def test_using_pager_from_config_when_env_config_both_set(clean_redis):
    config_content = dedent(
        f"""
        [main]
        log_location = /tmp/iredis1.log
        pager = {env_pager_numbers}
        """
    )

    with open(TEST_IREDISRC, "w+") as test_iredisrc:
        test_iredisrc.write(config_content)

    env = os.environ
    env["PAGER"] = env_pager
    child = pexpect.spawn(
        f"iredis -n 15 --iredisrc {TEST_IREDISRC}", timeout=3, env=env
    )
    child.logfile_read = open("cli_test.log", "ab")
    child.expect("127.0.0.1")
    for index in range(100):
        clean_redis.lpush("long-list", f"value-{index}")
    child.sendline("lrange long-list 0 -1")
    child.expect(TEST_PAGER_BOUNDARY_NUMBER)
    child.expect("value-1")
    child.expect(TEST_PAGER_BOUNDARY_NUMBER)
    child.close()
