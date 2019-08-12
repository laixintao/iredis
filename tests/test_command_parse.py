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


def test_command_cluster_delslots():
    judge("cluster delslots 1", {"command_slots": "cluster delslots", "slots": "1"})
    judge("CLUSTER DELSLOTS 1", {"command_slots": "CLUSTER DELSLOTS", "slots": "1"})
    judge(
        "cluster delslots 1 2 3 4",
        {"command_slots": "cluster delslots", "slots": "1 2 3 4"},
    )
    judge("cluster delslots 1 a", None)
    judge("cluster delslots a", None)
    judge("cluster delslots a 4", None)
    judge("cluster delslots abc", None)


def test_command_cluster_failover():
    judge(
        "cluster failover force",
        {"command_failoverchoice": "cluster failover", "failoverchoice": "force"},
    )
    judge(
        "cluster failover takeover",
        {"command_failoverchoice": "cluster failover", "failoverchoice": "takeover"},
    )
    judge(
        "CLUSTER FAILOVER FORCE",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "FORCE"},
    )
    judge(
        "CLUSTER FAILOVER takeover",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "takeover"},
    )
    judge(
        "CLUSTER FAILOVER TAKEOVER",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "TAKEOVER"},
    )


def test_command_cluster_forget():
    judge("cluster forget 1", {"command_node": "cluster forget", "node": "1"})
    judge(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command_node": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge("cluster forget 1 2 3 4", None)
    judge("cluster forget 1 a", None)
    judge("cluster forget a", None)
    judge("cluster forget a 2", None)
    judge("cluster forget abc", None)


def test_command_cluster_getkeysinslot():
    judge(
        "cluster getkeysinslot 1 1",
        {"command_slot_count": "cluster getkeysinslot", "slot": "1", "count": "1"},
    )
    judge(
        "CLUSTER GETKEYSINSLOT 1 1",
        {"command_slot_count": "CLUSTER GETKEYSINSLOT", "slot": "1", "count": "1"},
    )
    judge(
        "cluster getkeysinslot 1123 1121",
        {
            "command_slot_count": "cluster getkeysinslot",
            "slot": "1123",
            "count": "1121",
        },
    )
    judge("cluster getkeysinslot 1 2 3 4", None)
    judge("cluster getkeysinslot 1 a", None)
    judge("cluster getkeysinslot a", None)
    judge("cluster getkeysinslot a 4", None)
    judge("cluster getkeysinslot abc", None)
