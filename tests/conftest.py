import pexpect
import pytest
import redis
from iredis.client import Client
from iredis.commands_csv_loader import all_commands
from iredis.utils import split_command_args
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
                split_command_args(input_text, all_commands)
            return

        command, _ = split_command_args(input_text, all_commands)
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
    child = pexpect.spawn("iredis -n 15", timeout=TIMEOUT)
    child.logfile_read = open("cli_test.log", "ab")
    child.expect(["https://iredis.io/issues", "127.0.0.1"])
    yield child
    child.close()
