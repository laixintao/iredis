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


def test_command_cluster_addslots():
    judge("cluster addslots 1", {"command_slots": "cluster addslots", "slots": "1"})
    judge("CLUSTER ADDSLOTS 1", {"command_slots": "CLUSTER ADDSLOTS", "slots": "1"})
    judge(
        "cluster addslots 1 2 3 4",
        {"command_slots": "cluster addslots", "slots": "1 2 3 4"},
    )
    judge("cluster addslots 1 a", None)
    judge("cluster addslots a", None)
    judge("cluster addslots a 4", None)
    judge("cluster addslots abc", None)


def test_command_cluster_count_failure_reports():
    judge(
        "cluster count-failure-reports 1",
        {"command_node": "cluster count-failure-reports", "node": "1"},
    )
    judge(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command_node": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge("cluster count-failure-reports 1 2 3 4", None)
    judge("cluster count-failure-reports 1 a", None)
    judge("cluster count-failure-reports a", None)
    judge("cluster count-failure-reports a 2", None)
    judge("cluster count-failure-reports abc", None)


def test_command_cluster_countkeysinslot():
    judge(
        "cluster countkeysinslot 1",
        {"command_slot": "cluster countkeysinslot", "slot": "1"},
    )
    judge(
        "CLUSTER COUNTKEYSINSLOT 1",
        {"command_slot": "CLUSTER COUNTKEYSINSLOT", "slot": "1"},
    )
    judge("cluster countkeysinslot 1 2 3 4", None)
    judge("cluster countkeysinslot 1 a", None)
    judge("cluster countkeysinslot a", None)
    judge("cluster countkeysinslot a 4", None)
    judge("cluster countkeysinslot abc", None)
