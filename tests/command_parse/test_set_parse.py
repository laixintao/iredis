def test_sadd(judge_command):
    judge_command(
        "SADD foo m1 m2 m3", {"command": "SADD", "key": "foo", "members": "m1 m2 m3"}
    )
    judge_command("SADD foo m1", {"command": "SADD", "key": "foo", "members": "m1"})
    judge_command("SADD foo", None)


def test_sdiffstore(judge_command):
    judge_command(
        "SDIFFSTORE foo m1 m2 m3",
        {"command": "SDIFFSTORE", "destination": "foo", "keys": "m1 m2 m3"},
    )
    judge_command(
        "SDIFFSTORE foo m1",
        {"command": "SDIFFSTORE", "destination": "foo", "keys": "m1"},
    )
    judge_command("SDIFFSTORE foo", None)


def test_is_member(judge_command):
    judge_command("SISMEMBER foo m1 m2 m3", None)
    judge_command(
        "SISMEMBER foo m1", {"command": "SISMEMBER", "key": "foo", "member": "m1"}
    )
    judge_command("SISMEMBER foo", None)


def test_smove(judge_command):
    judge_command(
        "SMOVE foo bar m2",
        {"command": "SMOVE", "key": "foo", "newkey": "bar", "member": "m2"},
    )
    judge_command("SMOVE foo m1", None)
    judge_command("SMOVE foo", None)


def test_spop(judge_command):
    judge_command("SPOP set", {"command": "SPOP", "key": "set"})
    judge_command("SPOP set 3", {"command": "SPOP", "key": "set", "count": "3"})
