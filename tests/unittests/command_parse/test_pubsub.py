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
        {"command": "PUBSUB CHANNELS"},
    )
    judge_command(
        "PUBSUB NUMSUB",
        {"command": "PUBSUB NUMSUB"},
    )
    judge_command(
        "PUBSUB NUMSUB foo bar",
        {"command": "PUBSUB NUMSUB", "parameters": "foo bar"},
    )
    judge_command(
        "PUBSUB CHANNELS mypattern",
        {"command": "PUBSUB CHANNELS", "parameters": "mypattern"},
    )


def test_punsubscribe(judge_command):
    """PUNSUBSCRIBE accepts 0 or more patterns (per commands.json)."""
    judge_command("PUNSUBSCRIBE", {"command": "PUNSUBSCRIBE"})
    judge_command(
        "PUNSUBSCRIBE p1 p2",
        {"command": "PUNSUBSCRIBE", "channel": "p2"},
    )


def test_unsubscribe(judge_command):
    """UNSUBSCRIBE accepts 0 or more channels (per commands.json)."""
    judge_command("UNSUBSCRIBE", {"command": "UNSUBSCRIBE"})
    judge_command(
        "UNSUBSCRIBE c1 c2",
        {"command": "UNSUBSCRIBE", "channel": "c2"},
    )
