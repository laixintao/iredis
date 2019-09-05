import pexpect
import pytest
import redis
import time
import threading
from unittest.mock import MagicMock
from iredis.entry import compile_grammar_bg
from iredis.redis_grammar import REDIS_COMMANDS
from iredis.client import Client
from iredis.completers import get_completer
from iredis.commands_csv_loader import group2commands
from prompt_toolkit.contrib.regular_languages.compiler import compile


TIMEOUT = 3
redis_grammar = compile(REDIS_COMMANDS)
HISTORY_FILE = ".iredis_history"


@pytest.fixture
def completer():
    return get_completer(group2commands, redis_grammar)


@pytest.fixture
def judge_command():
    def judge_command_func(command, expect):
        m = redis_grammar.match(command)

        # not match
        if not expect:
            assert m is None
            return

        variables = m.variables()
        for expect_token, expect_value in expect.items():
            all_variables = variables.getall(expect_token)
            if len(all_variables) > 1:
                assert sorted(all_variables) == sorted(expect_value)
            else:
                assert variables.get(expect_token) == expect_value

    return judge_command_func


@pytest.fixture
def clean_redis():
    """
    Return a empty redis db. (redis-py client)
    """
    client = redis.StrictRedis(db=15)
    client.flushdb()
    return client


@pytest.fixture
def iredis_client():
    return Client("127.0.0.1", "6379", None)


@pytest.fixture(scope="module")
def local_process():
    """Open iredis subprocess to test"""
    child = pexpect.spawn("iredis -n 15", timeout=TIMEOUT)
    yield child
    child.close()


def prompt_session():
    """Global prompt-toolkit session, compiled grammer"""
    session = MagicMock()
    normal_thread_count = threading.active_count()
    compile_grammar_bg(session)
    while threading.active_count() > normal_thread_count:
        time.sleep(0.1)
    return session
