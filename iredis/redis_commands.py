REDIS_COMMANDS = r"""
(\s*  (?P<command_key>(HGETALL|GET))   \s+   (?P<key>[0-9.]+)   \s*) |
(\s*  (?P<command_key_value>(SET|KSET))   \s+   (?P<key>[0-9.]+)   \s+   (?P<value>[0-9.]+)   \s*) 
"""
