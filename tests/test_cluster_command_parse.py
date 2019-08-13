"""
redis command in `cluster` group parse test.
"""


def test_command_cluster_addslots(judge_command):
    judge_command(
        "cluster addslots 1", {"command_slots": "cluster addslots", "slots": "1"}
    )
    judge_command(
        "CLUSTER ADDSLOTS 1", {"command_slots": "CLUSTER ADDSLOTS", "slots": "1"}
    )
    judge_command(
        "cluster addslots 1 2 3 4",
        {"command_slots": "cluster addslots", "slots": "1 2 3 4"},
    )
    judge_command("cluster addslots 1 a", None)
    judge_command("cluster addslots a", None)
    judge_command("cluster addslots a 4", None)
    judge_command("cluster addslots abc", None)


def test_command_cluster_count_failure_reports(judge_command):
    judge_command(
        "cluster count-failure-reports 1",
        {"command_node": "cluster count-failure-reports", "node": "1"},
    )
    judge_command(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command_node": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge_command("cluster count-failure-reports 1 2 3 4", None)
    judge_command("cluster count-failure-reports 1 a", None)
    judge_command("cluster count-failure-reports a", None)
    judge_command("cluster count-failure-reports a 2", None)
    judge_command("cluster count-failure-reports abc", None)


def test_command_cluster_countkeysinslot(judge_command):
    judge_command(
        "cluster countkeysinslot 1",
        {"command_slot": "cluster countkeysinslot", "slot": "1"},
    )
    judge_command(
        "CLUSTER COUNTKEYSINSLOT 1",
        {"command_slot": "CLUSTER COUNTKEYSINSLOT", "slot": "1"},
    )
    judge_command("cluster countkeysinslot 1 2 3 4", None)
    judge_command("cluster countkeysinslot 1 a", None)
    judge_command("cluster countkeysinslot a", None)
    judge_command("cluster countkeysinslot a 4", None)
    judge_command("cluster countkeysinslot abc", None)


def test_command_cluster_delslots(judge_command):
    judge_command(
        "cluster delslots 1", {"command_slots": "cluster delslots", "slots": "1"}
    )
    judge_command(
        "CLUSTER DELSLOTS 1", {"command_slots": "CLUSTER DELSLOTS", "slots": "1"}
    )
    judge_command(
        "cluster delslots 1 2 3 4",
        {"command_slots": "cluster delslots", "slots": "1 2 3 4"},
    )
    judge_command("cluster delslots 1 a", None)
    judge_command("cluster delslots a", None)
    judge_command("cluster delslots a 4", None)
    judge_command("cluster delslots abc", None)


def test_command_cluster_failover(judge_command):
    judge_command(
        "cluster failover force",
        {"command_failoverchoice": "cluster failover", "failoverchoice": "force"},
    )
    judge_command(
        "cluster failover takeover",
        {"command_failoverchoice": "cluster failover", "failoverchoice": "takeover"},
    )
    judge_command(
        "CLUSTER FAILOVER FORCE",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "FORCE"},
    )
    judge_command(
        "CLUSTER FAILOVER takeover",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "takeover"},
    )
    judge_command(
        "CLUSTER FAILOVER TAKEOVER",
        {"command_failoverchoice": "CLUSTER FAILOVER", "failoverchoice": "TAKEOVER"},
    )


def test_command_cluster_forget(judge_command):
    judge_command("cluster forget 1", {"command_node": "cluster forget", "node": "1"})
    judge_command(
        "CLUSTER COUNT-FAILURE-REPORTS 1",
        {"command_node": "CLUSTER COUNT-FAILURE-REPORTS", "node": "1"},
    )
    judge_command("cluster forget 1 2 3 4", None)
    judge_command("cluster forget 1 a", None)
    judge_command("cluster forget a", None)
    judge_command("cluster forget a 2", None)
    judge_command("cluster forget abc", None)


def test_command_cluster_getkeysinslot(judge_command):
    judge_command(
        "cluster getkeysinslot 1 1",
        {"command_slot_count": "cluster getkeysinslot", "slot": "1", "count": "1"},
    )
    judge_command(
        "CLUSTER GETKEYSINSLOT 1 1",
        {"command_slot_count": "CLUSTER GETKEYSINSLOT", "slot": "1", "count": "1"},
    )
    judge_command(
        "cluster getkeysinslot 1123 1121",
        {
            "command_slot_count": "cluster getkeysinslot",
            "slot": "1123",
            "count": "1121",
        },
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
    judge_command("Acluster info", None)


def test_command_cluster_keyslot(judge_command):
    judge_command(
        "cluster keyslot mykey", {"command_key": "cluster keyslot", "key": "mykey"}
    )
    judge_command(
        "cluster keyslot MYKEY", {"command_key": "cluster keyslot", "key": "MYKEY"}
    )
    judge_command(
        "CLUSTER KEYSLOT MYKEY", {"command_key": "CLUSTER KEYSLOT", "key": "MYKEY"}
    )


def test_command_cluster_meet(judge_command):
    judge_command(
        "cluster meet 192.168.0.1 12200",
        {"command_ip_port": "cluster meet", "ip": "192.168.0.1", "port": "12200"},
    )
    judge_command(
        "CLUSTER MEET 192.168.0.1 12200",
        {"command_ip_port": "CLUSTER MEET", "ip": "192.168.0.1", "port": "12200"},
    )


def test_command_cluster_nodes(judge_command):
    judge_command("cluster nodes", {"command": "cluster nodes"})
    judge_command("CLUSTER NODES", {"command": "CLUSTER NODES"})


def test_command_cluster_reset(judge_command):
    judge_command(
        "cluster reset hard",
        {"command_resetchoice": "cluster reset", "resetchoice": "hard"},
    )
    judge_command(
        "cluster reset soft",
        {"command_resetchoice": "cluster reset", "resetchoice": "soft"},
    )
    judge_command(
        "CLUSTER RESET HARD",
        {"command_resetchoice": "CLUSTER RESET", "resetchoice": "HARD"},
    )
    judge_command(
        "CLUSTER RESET soft",
        {"command_resetchoice": "CLUSTER RESET", "resetchoice": "soft"},
    )
    judge_command(
        "CLUSTER RESET SOFT",
        {"command_resetchoice": "CLUSTER RESET", "resetchoice": "SOFT"},
    )
    judge_command("CLUSTER RESET SOFT1", None)
    judge_command("CLUSTER RESET SAOFT", None)


def test_command_cluster_set_config_epoch(judge_command):
    judge_command("cluster set-config-epoch 123123 ad", None)
    judge_command(
        "cluster set-config-epoch 0 ",
        {"command_epoch": "cluster set-config-epoch", "epoch": "0"},
    )
    judge_command(
        "cluster set-config-epoch 123123 ",
        {"command_epoch": "cluster set-config-epoch", "epoch": "123123"},
    )
