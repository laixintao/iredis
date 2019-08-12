VALID_TOKEN = r"""(
("([^"]|\\")*?")     |# with quotes
([^\s"]+)             # without quotes
)"""
VALID_SLOT = """\d+"""  # TODO add range? max value:16384
SLOT = f"""(?P<slot>{VALID_SLOT})"""
SLOTS = f"""(?P<slots>{VALID_SLOT}(\s+{VALID_SLOT})*)"""
KEY = f"""(?P<key>{VALID_TOKEN})"""
VALUE = f"""(?P<value>{VALID_TOKEN})"""
FIELDS = f"""(?P<fields>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"""

REDIS_COMMANDS = f"""
(\s*  (?P<command_slots>({command_slots}))        \s+ {SLOTS}                                    \s*)|

(\s*  (?P<command_key>(HGETALL|GET))      \s+  {KEY}                                    \s*)|
(\s*  (?P<command_key_fields>(HDEL))      \s+  {KEY}  \s+ {FIELDS}                      \s*)|
(\s*  (?P<command_key_value>(SET|KSET|HAAA))   \s+   {KEY}   \s+   {VALUE}                \s*) 
"""
