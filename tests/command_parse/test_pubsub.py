def test_publish(judge_command):
    judge_command(
        "publish foo bar",
        {"command_channel_message": "publish", "channel": "foo", "message": "bar"},
    )


def test_subscribe(judge_command):
    judge_command(
        "subscribe foo bar", {"command_channels": "subscribe", "channel": "bar"}
    )


def test_pubsub(judge_command):
    judge_command(
        "PUBSUB NUMSUB foo bar",
        {
            "command_pubsubcmd_channels": "PUBSUB",
            "pubsubcmd": "NUMSUB",
            "channel": "bar",
        },
    )
