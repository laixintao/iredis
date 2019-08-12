from prompt_toolkit.contrib.regular_languages.compiler import compile
from .commands_csv_loader import t

VALID_TOKEN = r"""(
("([^"]|\\")*?")     |# with quotes
([^\s"]+)             # without quotes
)"""
VALID_SLOT = """\d+"""  # TODO add range? max value:16384
VALID_NODE = "\d+"
SLOT = f"""(?P<slot>{VALID_SLOT})"""
SLOTS = f"""(?P<slots>{VALID_SLOT}(\s+{VALID_SLOT})*)"""
NODE = f"(?P<node>{VALID_NODE})"
KEY = f"""(?P<key>{VALID_TOKEN})"""
VALUE = f"""(?P<value>{VALID_TOKEN})"""
FIELDS = f"""(?P<fields>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"""


REDIS_COMMANDS = f"""
(\s*  (?P<command_slots>({t['command_slots']}))        \s+ {SLOTS}                                    \s*)|
(\s*  (?P<command_node>({t['command_node']}))          \s+ {NODE}                                     \s*)|
(\s*  (?P<command_slot>({t['command_slot']}))          \s+ {SLOT}                                     \s*)|

(\s*  (?P<command_key>(HGETALL|GET))      \s+  {KEY}                                    \s*)|
(\s*  (?P<command_key_fields>(HDEL))      \s+  {KEY}  \s+ {FIELDS}                      \s*)|
(\s*  (?P<command_key_value>(SET|KSET|HAAA))   \s+   {KEY}   \s+   {VALUE}                \s*) 
"""

redis_grammar = compile(REDIS_COMMANDS)
