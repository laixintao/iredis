def test_sadd(judge_command):
    judge_command(
        "SADD foo m1 m2 m3",
        {"command_key_members": "SADD", "key": "foo", "members": "m1 m2 m3"},
    )
    judge_command(
        "SADD foo m1", {"command_key_members": "SADD", "key": "foo", "members": "m1"}
    )
    judge_command("SADD foo", None)


def test_sdiffstore(judge_command):
    judge_command(
        "SDIFFSTORE foo m1 m2 m3",
        {
            "command_destination_keys": "SDIFFSTORE",
            "destination": "foo",
            "keys": "m1 m2 m3",
        },
    )
    judge_command(
        "SDIFFSTORE foo m1",
        {"command_destination_keys": "SDIFFSTORE", "destination": "foo", "keys": "m1"},
    )
    judge_command("SDIFFSTORE foo", None)


def test_is_member(judge_command):
    judge_command("SISMEMBER foo m1 m2 m3", None)
    judge_command(
        "SISMEMBER foo m1",
        {"command_key_member": "SISMEMBER", "key": "foo", "member": "m1"},
    )
    judge_command("SISMEMBER foo", None)
