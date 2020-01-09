def test_publish(judge_command):
    judge_command(
        "publish foo bar", {"command": "publish", "channel": "foo", "message": "bar"}
    )


def test_subscribe(judge_command):
    judge_command("subscribe foo bar", {"command": "subscribe", "channel": "bar"})


def test_pubsub(judge_command):
    judge_command(
        "PUBSUB NUMSUB foo bar",
        {"command": "PUBSUB", "pubsubcmd": "NUMSUB", "channel": "bar"},
    )
