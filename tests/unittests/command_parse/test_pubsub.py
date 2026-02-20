def test_publish(judge_command):
    judge_command(
        "publish foo bar", {"command": "publish", "channel": "foo", "message": "bar"}
    )


def test_subscribe(judge_command):
    judge_command("subscribe foo bar", {"command": "subscribe", "channel": "bar"})


def test_pubsub(judge_command):
    """PUBSUB CHANNELS/NUMSUB/NUMPAT accept 0 or more channels (per commands.json)."""
    judge_command(
        "PUBSUB CHANNELS",
        {"command": "PUBSUB", "pubsubcmd": "CHANNELS"},
    )
    judge_command(
        "PUBSUB NUMSUB",
        {"command": "PUBSUB", "pubsubcmd": "NUMSUB"},
    )
    judge_command(
        "PUBSUB NUMSUB foo bar",
        {"command": "PUBSUB", "pubsubcmd": "NUMSUB", "channel": "bar"},
    )
    judge_command(
        "PUBSUB CHANNELS mypattern",
        {"command": "PUBSUB", "pubsubcmd": "CHANNELS", "channel": "mypattern"},
    )
