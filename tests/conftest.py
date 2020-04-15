import os
import tempfile
from textwrap import dedent

import pexpect
import pytest
import redis

from iredis.client import Client
from iredis.commands import split_command_args
from iredis.redis_grammar import get_command_grammar
from iredis.exceptions import InvalidArguments
from iredis.config import Config, config as global_config


TIMEOUT = 2
HISTORY_FILE = ".iredis_history"


@pytest.fixture
def judge_command():
    def judge_command_func(input_text, expect):
        if expect == "invalid":
            with pytest.raises(InvalidArguments):
                split_command_args(input_text)
            return

        command, _ = split_command_args(input_text)
        grammar = get_command_grammar(command)

        m = grammar.match(input_text)

        # test on not match
        if not expect:
            assert m is None
            return

        variables = m.variables()
        print("Found variables: {}".format(variables))
        for expect_token, expect_value in expect.items():
            all_variables = variables.getall(expect_token)
            if len(all_variables) > 1:
                assert sorted(all_variables) == sorted(expect_value)
            else:
                assert variables.get(expect_token) == expect_value

    return judge_command_func


@pytest.fixture(scope="function")
def clean_redis():
    """
    Return a empty redis db. (redis-py client)
    """
    client = redis.StrictRedis(db=15)
    client.flushdb()
    return client


@pytest.fixture
def iredis_client():
    return Client("127.0.0.1", "6379", db=15)


@pytest.fixture
def config():
    newconfig = Config()
    global_config.__dict__ = newconfig.__dict__
    config.raw = False
    return global_config


@pytest.fixture(scope="function")
def cli():
    """Open iredis subprocess to test"""
    f = tempfile.TemporaryFile("w")
    config_content = dedent(
        """
        [main]
        log_location =
        warning = True
        """
    )
    f.write(config_content)
    f.close()
    env = os.environ
    env["PROMPT_TOOLKIT_NO_CPR"] = "1"

    child = pexpect.spawn(f"iredis -n 15 --iredisrc {f.name}", timeout=TIMEOUT, env=env)
    child.logfile_read = open("cli_test.log", "ab")
    child.expect(["https://iredis.io/issues", "127.0.0.1"])
    yield child
    child.close()


@pytest.fixture(scope="function")
def raw_cli():
    """Open iredis subprocess to test"""
    TEST_IREDISRC = "/tmp/.iredisrc.test"
    config_content = dedent(
        """
        [main]
        log_location =
        warning = True
        """
    )

    with open(TEST_IREDISRC, "w+") as test_iredisrc:
        test_iredisrc.write(config_content)

    child = pexpect.spawn(
        f"iredis --raw -n 15 --iredisrc {TEST_IREDISRC}", timeout=TIMEOUT
    )
    child.logfile_read = open("cli_test.log", "ab")
    child.expect(["https://iredis.io/issues", "127.0.0.1"])
    yield child
    child.close()


@pytest.fixture(scope="function")
def cli_without_warning():
    f = tempfile.TemporaryFile("w")
    config_content = dedent(
        """
        [main]
        log_location = /tmp/iredis1.log
        warning = False
        """
    )
    f.write(config_content)
    f.close()

    cli = pexpect.spawn(f"iredis -n 15 --iredisrc {f.name}", timeout=1)
    cli.logfile_read = open("cli_test.log", "ab")
    yield cli
    cli.close()
    os.remove("/tmp/iredisrc")
