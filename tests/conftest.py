import pytest
from iredis.redis_grammar import redis_grammar


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
