def test_publish(judge_command):
    judge_command(
        "publish foo bar",
        {"command_channel_message": "publish", "channel": "foo", "message": "bar"},
    )
