from iredis.redis_grammar import redis_grammar


def judge(command, expect):
    m = redis_grammar.match(command)

    # not match
    if not expect:
        assert m is None
        return

    variables = m.variables()
    for expect_token, expect_value in expect.items():
        assert variables.get(expect_token) == expect_value


def test_command_slots():
    judge("cluster addslots 1", {"command_slots": "cluster addslots", "slots": "1"})
    judge(
        "cluster addslots 1 2 3 4",
        {"command_slots": "cluster addslots", "slots": "1 2 3 4"},
    )
    judge("cluster addslots 1 a", None)
    judge("cluster addslots a", None)
    judge("cluster addslots a 2", None)
    judge("cluster addslots abc", None)
