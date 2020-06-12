def test_client_setname(judge_command):
    judge_command(
        "CLIENT SETNAME foobar", {"command": "CLIENT SETNAME", "value": "foobar"}
    )


def test_client_unblock(judge_command):
    judge_command(
        "CLIENT UNBLOCK 33 TIMEOUT",
        {"command": "CLIENT UNBLOCK", "clientid": "33", "error": "TIMEOUT"},
    )
    judge_command("CLIENT UNBLOCK 33", {"command": "CLIENT UNBLOCK", "clientid": "33"})


def test_flushdb(judge_command):
    judge_command("FLUSHDB async", {"command": "FLUSHDB", "async": "async"})
    judge_command("FLUSHDB", {"command": "FLUSHDB"})
    judge_command("FLUSHDB ASYNC", {"command": "FLUSHDB", "async": "ASYNC"})
    judge_command("FLUSHALL ASYNC", {"command": "FLUSHALL", "async": "ASYNC"})


def test_client_list(judge_command):
    judge_command("client list", {"command": "client list"})
    judge_command("client list TYPE REPLICA1", None)
    judge_command(
        "client list type master",
        {"command": "client list", "type_const": "type", "conntype": "master"},
    )
    judge_command(
        "client list TYPE REPLICA",
        {"command": "client list", "type_const": "TYPE", "conntype": "REPLICA"},
    )


def test_configset(judge_command):
    judge_command(
        "config set foo bar",
        {"command": "config set", "parameter": "foo", "value": "bar"},
    )
    judge_command(
        "config set requirepass ''",
        {"command": "config set", "parameter": "requirepass", "value": "''"},
    )


def test_shutdown(judge_command):
    judge_command("shutdown save", {"command": "shutdown", "shutdown": "save"})
    judge_command("shutdown NOSAVE", {"command": "shutdown", "shutdown": "NOSAVE"})


def test_clientpause(judge_command):
    judge_command("client pause 3000", {"command": "client pause", "timeout": "3000"})


def test_client_reply(judge_command):
    judge_command("client reply on", {"command": "client reply", "switch": "on"})


def test_client_kill(judge_command):
    judge_command(
        "CLIENT KILL addr 127.0.0.1:12345 type pubsub",
        {
            "command": "CLIENT KILL",
            "addr": "addr",
            "ip_port": "127.0.0.1:12345",
            "type_const": "type",
            "conntype": "pubsub",
        },
    )
    judge_command(
        "CLIENT KILL 127.0.0.1:12345 ",
        {"command": "CLIENT KILL", "ip_port": "127.0.0.1:12345"},
    )
    judge_command(
        "CLIENT KILL id 123455 type pubsub skipme no",
        {
            "command": "CLIENT KILL",
            "const_id": "id",
            "clientid": "123455",
            "type_const": "type",
            "conntype": "pubsub",
            "skipme": "skipme",
            "yes": "no",
        },
    )


def test_client_kill_username(judge_command):
    """since redis-server 6.0"""
    judge_command(
        "client kill USER default",
        {"command": "client kill", "const_user": "USER", "username": "default"},
    )


def test_client_kill_unordered_arguments(judge_command):
    judge_command(
        "CLIENT KILL type pubsub addr 127.0.0.1:12345",
        {
            "command": "CLIENT KILL",
            "addr": "addr",
            "ip_port": "127.0.0.1:12345",
            "type_const": "type",
            "conntype": "pubsub",
        },
    )


def test_psync(judge_command):
    judge_command(
        "PSYNC abc 123", {"command": "PSYNC", "replicationid": "abc", "offset": "123"}
    )
    judge_command("PSYNC", None)


def test_latency_graph(judge_command):
    judge_command(
        "latency graph command", {"command": "latency graph", "graphevent": "command"}
    )
    judge_command(
        "latency graph fork", {"command": "latency graph", "graphevent": "fork"}
    )
    judge_command("latency graph", None)


def test_latency_reset(judge_command):
    judge_command(
        "latency reset command fork aof-fsync-always",
        {"command": "latency reset", "graphevent": "aof-fsync-always"},
    )
    judge_command(
        "latency reset fork", {"command": "latency reset", "graphevent": "fork"}
    )
    judge_command("latency reset", {"command": "latency reset"})


def test_lolwut(judge_command):
    judge_command("lolwut", {"command": "lolwut"})
    # only works before redis 6
    judge_command("lolwut 5", {"command": "lolwut", "any": "5"})
    judge_command("lolwut 5 1", {"command": "lolwut", "any": "5 1"})
    # redis 6
    judge_command(
        "lolwut VERSION 5 5",
        {"command": "lolwut", "version": "VERSION", "version_num": "5", "any": "5"},
    )


def test_info(judge_command):
    judge_command("info cpu", {"command": "info", "section": "cpu"})
    judge_command("info", {"command": "info"})
    judge_command("info all", {"command": "info", "section": "all"})
    judge_command("info CPU", {"command": "info", "section": "CPU"})


def test_bgsave(judge_command):
    judge_command("bgsave", {"command": "bgsave"})
    judge_command("bgsave schedule", {"command": "bgsave", "schedule": "schedule"})
    judge_command("BGSAVE SCHEDULE", {"command": "BGSAVE", "schedule": "SCHEDULE"})


def test_acl_cat(judge_command):
    judge_command("acl cat", {"command": "acl cat"})
    judge_command("acl  CAT", {"command": "acl  CAT"})
    judge_command(
        "ACL CAT scripting", {"command": "ACL CAT", "categoryname": "scripting"}
    )
    judge_command("ACL CAT WATCH", {"command": "ACL CAT", "categoryname": "WATCH"})


def test_acl_deluser(judge_command):
    judge_command(
        "acl deluser laixintao", {"command": "acl deluser", "username": "laixintao"}
    )
    judge_command(
        "acl deluser laixintao antirez",
        {"command": "acl deluser", "username": "antirez"},
    )


def test_acl_log(judge_command):
    judge_command("acl log 2", {"command": "acl log", "count": "2"})
    judge_command("acl log reset", {"command": "acl log", "reset_const": "reset"})
    judge_command("acl log ", {"command": "acl log"})


def test_acl_setuser(judge_command):
    judge_command("ACL SETUSER alice", {"command": "ACL SETUSER", "username": "alice"})
    judge_command(
        "ACL SETUSER alice on >p1pp0 ~cached:* +get",
        {"command": "ACL SETUSER", "username": "alice", "rule": "+get"},
    )
    judge_command(
        "ACL SETUSER alan allkeys +@string +@set -SADD >alanpassword",
        {"command": "ACL SETUSER", "username": "alan", "rule": ">alanpassword"},
    )


def test_acl_getuser(judge_command):
    judge_command("acl getuser alan", {"command": "acl getuser", "username": "alan"})
    judge_command("acl getuser", None)
