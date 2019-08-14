def test_del(judge_command):
    judge_command("DEL abc", {"command_key": "DEL", "key": "abc"})
    judge_command("DEL bc1", {"command_key": "DEL", "key": "bc1"})
    judge_command("DEL 1", {"command_key": "DEL", "key": "1"})
    judge_command("DEL 1 2", None)
    judge_command('DEL "hello world"', {"command_key": "DEL", "key": '"hello world"'})
    judge_command(
        r'DEL "hell\"o world"', {"command_key": "DEL", "key": r'"hell\"o world"'}
    )
