def test_eval(judge_command):
    judge_command(
        'eval "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}" 2 key1 key2 first second',
        {
            "command_lua_any": "eval",
            "double_lua": "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}",
            "any": "2 key1 key2 first second",
        },
    )
    judge_command(
        "eval 'return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}' 2 key1 key2 first second",
        {
            "command_lua_any": "eval",
            "single_lua": "return {KEYS[1],KEYS[2],ARGV[1],ARGV[2]}",
            "any": "2 key1 key2 first second",
        },
    )
