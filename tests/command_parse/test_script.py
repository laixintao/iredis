def test_eval(judge_command):
    judge_command(
        'eval "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}" 2 key1 key2 first second',
        {
            "command": "eval",
            "double_lua": "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}",
            "any": "2 key1 key2 first second",
        },
    )
    judge_command(
        "eval 'return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}' 2 key1 key2 first second",
        {
            "command": "eval",
            "single_lua": "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}",
            "any": "2 key1 key2 first second",
        },
    )


def test_scriptdebug(judge_command):
    judge_command("SCRIPT DEBUG YES", {"command": "SCRIPT DEBUG", "scriptdebug": "YES"})
    judge_command("SCRIPT DEBUG no", {"command": "SCRIPT DEBUG", "scriptdebug": "no"})
