"""
redis command in `cluster` group parse test.
"""


def test_command_cluster_addslots(judge_command):
    judge_command("cluster addslots 1", {"command": "cluster addslots", "slots": "1"})
    judge_command("CLUSTER ADDSLOTS 1", {"command": "CLUSTER ADDSLOTS", "slots": "1"})
    judge_command(
        "cluster addslots 1 2 3 4", {"command": "cluster addslots", "slots": "1 2 3 4"}
    )
    judge_command("cluster addslots 1 a", None)
    judge_command("cluster addslots a", None)
    judge_command("cluster addslots a 4", None)
    judge_command("cluster addslots abc", None)


def test_command_cluster_count_failure_reports(judge_command):
    judge_command(
        "cluster count-failure-reports 1",
        {"command": "cluster count-failure-reports", "node": "1"},
    )
    judge_command(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge_command("cluster count-failure-reports 1 2 3 4", None)
    judge_command("cluster count-failure-reports 1 a", None)
    judge_command(
        "cluster count-failure-reports a",
        {"command": "cluster count-failure-reports", "node": "a"},
    )
    judge_command("cluster count-failure-reports a 2", None)
    judge_command(
        "cluster count-failure-reports abc",
        {"command": "cluster count-failure-reports", "node": "abc"},
    )


def test_command_cluster_countkeysinslot(judge_command):
    judge_command(
        "cluster countkeysinslot 1", {"command": "cluster countkeysinslot", "slot": "1"}
    )
    judge_command(
        "CLUSTER COUNTKEYSINSLOT 1", {"command": "CLUSTER COUNTKEYSINSLOT", "slot": "1"}
    )
    judge_command("cluster countkeysinslot 1 2 3 4", None)
    judge_command("cluster countkeysinslot 1 a", None)
    judge_command("cluster countkeysinslot a", None)
    judge_command("cluster countkeysinslot a 4", None)
    judge_command("cluster countkeysinslot abc", None)


def test_command_cluster_delslots(judge_command):
    judge_command("cluster delslots 1", {"command": "cluster delslots", "slots": "1"})
    judge_command("CLUSTER DELSLOTS 1", {"command": "CLUSTER DELSLOTS", "slots": "1"})
    judge_command(
        "cluster delslots 1 2 3 4", {"command": "cluster delslots", "slots": "1 2 3 4"}
    )
    judge_command("cluster delslots 1 a", None)
    judge_command("cluster delslots a", None)
    judge_command("cluster delslots a 4", None)
    judge_command("cluster delslots abc", None)


def test_command_cluster_failover(judge_command):
    judge_command(
        "cluster failover force",
        {"command": "cluster failover", "failoverchoice": "force"},
    )
    judge_command(
        "cluster failover takeover",
        {"command": "cluster failover", "failoverchoice": "takeover"},
    )
    judge_command(
        "CLUSTER FAILOVER FORCE",
        {"command": "CLUSTER FAILOVER", "failoverchoice": "FORCE"},
    )
    judge_command(
        "CLUSTER FAILOVER takeover",
        {"command": "CLUSTER FAILOVER", "failoverchoice": "takeover"},
    )
    judge_command(
        "CLUSTER FAILOVER TAKEOVER",
        {"command": "CLUSTER FAILOVER", "failoverchoice": "TAKEOVER"},
    )


def test_command_cluster_forget(judge_command):
    judge_command("cluster forget 1", {"command": "cluster forget", "node": "1"})
    judge_command(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge_command("cluster forget 1 2 3 4", None)
    judge_command("cluster forget 1 a", None)
    judge_command("cluster forget a", {"command": "cluster forget", "node": "a"})
    judge_command("cluster forget a 2", None)
    judge_command(
        "cluster forget abc",
        {
            "command": "cluster forget",
            "node": "abc",
        },
    )
    judge_command(
        "cluster forget 07c37dfeb235213a872192d90877d0cd55635b91",
        {
            "command": "cluster forget",
            "node": "07c37dfeb235213a872192d90877d0cd55635b91",
        },
    )


def test_command_cluster_getkeysinslot(judge_command):
    judge_command(
        "cluster getkeysinslot 1 1",
        {"command": "cluster getkeysinslot", "slot": "1", "count": "1"},
    )
    judge_command(
        "CLUSTER GETKEYSINSLOT 1 1",
        {"command": "CLUSTER GETKEYSINSLOT", "slot": "1", "count": "1"},
    )
    judge_command(
        "cluster getkeysinslot 1123 1121",
        {"command": "cluster getkeysinslot", "slot": "1123", "count": "1121"},
    )
    judge_command("cluster getkeysinslot 1 2 3 4", None)
    judge_command("cluster getkeysinslot 1 a", None)
    judge_command("cluster getkeysinslot a", None)
    judge_command("cluster getkeysinslot a 4", None)
    judge_command("cluster getkeysinslot abc", None)


def test_command_cluster_info(judge_command):
    judge_command("cluster info", {"command": "cluster info"})
    judge_command("CLUSTER INFO", {"command": "CLUSTER INFO"})
    judge_command("CLUSTER INFO 1", None)
    judge_command("Acluster info", "invalid")


def test_command_cluster_keyslot(judge_command):
    judge_command(
        "cluster keyslot mykey", {"command": "cluster keyslot", "key": "mykey"}
    )
    judge_command(
        "cluster keyslot MYKEY", {"command": "cluster keyslot", "key": "MYKEY"}
    )
    judge_command(
        "CLUSTER KEYSLOT MYKEY", {"command": "CLUSTER KEYSLOT", "key": "MYKEY"}
    )


def test_command_cluster_meet(judge_command):
    judge_command(
        "cluster meet 192.168.0.1 12200",
        {"command": "cluster meet", "ip": "192.168.0.1", "port": "12200"},
    )
    judge_command(
        "CLUSTER MEET 192.168.0.1 12200",
        {"command": "CLUSTER MEET", "ip": "192.168.0.1", "port": "12200"},
    )


def test_command_cluster_nodes(judge_command):
    judge_command("cluster nodes", {"command": "cluster nodes"})
    judge_command("CLUSTER NODES", {"command": "CLUSTER NODES"})


def test_command_cluster_reset(judge_command):
    judge_command(
        "cluster reset hard", {"command": "cluster reset", "resetchoice": "hard"}
    )
    judge_command(
        "cluster reset soft", {"command": "cluster reset", "resetchoice": "soft"}
    )
    judge_command(
        "CLUSTER RESET HARD", {"command": "CLUSTER RESET", "resetchoice": "HARD"}
    )
    judge_command(
        "CLUSTER RESET soft", {"command": "CLUSTER RESET", "resetchoice": "soft"}
    )
    judge_command(
        "CLUSTER RESET SOFT", {"command": "CLUSTER RESET", "resetchoice": "SOFT"}
    )
    judge_command("CLUSTER RESET SOFT1", None)
    judge_command("CLUSTER RESET SAOFT", None)


def test_command_cluster_set_config_epoch(judge_command):
    judge_command("cluster set-config-epoch 123123 ad", None)
    judge_command(
        "cluster set-config-epoch 0 ",
        {"command": "cluster set-config-epoch", "epoch": "0"},
    )
    judge_command(
        "cluster set-config-epoch 123123 ",
        {"command": "cluster set-config-epoch", "epoch": "123123"},
    )


def test_command_cluster_set_slot(judge_command):
    judge_command(
        "cluster setslot 123 importing 123123",
        {
            "command": "cluster setslot",
            "slot": "123",
            "slotsubcmd": "importing",
            "node": "123123",
        },
    )
    judge_command(
        "cluster setslot 123 migrating 123123",
        {
            "command": "cluster setslot",
            "slot": "123",
            "slotsubcmd": "migrating",
            "node": "123123",
        },
    )
    judge_command(
        "cluster setslot 123 node 123123",
        {
            "command": "cluster setslot",
            "slot": "123",
            "slotsubcmd": "node",
            "node": "123123",
        },
    )
    judge_command(
        "cluster setslot 123 node e7d1eecce10fd6bb5eb35b9f99a514335d9ba9ca",
        {
            "command": "cluster setslot",
            "slot": "123",
            "slotsubcmd": "node",
            "node": "e7d1eecce10fd6bb5eb35b9f99a514335d9ba9ca",
        },
    )
    judge_command(
        "cluster setslot 123 MIGRATING 123123",
        {
            "command": "cluster setslot",
            "slot": "123",
            "slotsubcmd": "MIGRATING",
            "node": "123123",
        },
    )
    judge_command(
        "cluster setslot 123 stable",
        {"command": "cluster setslot", "slot": "123", "slotsubcmd": "stable"},
    )
    judge_command(
        "cluster setslot 123 STABLE",
        {"command": "cluster setslot", "slot": "123", "slotsubcmd": "STABLE"},
    )
