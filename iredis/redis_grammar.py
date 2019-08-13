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
FAILOVERCHOICE = (
    "(?P<failoverchoice>(FORCE|TAKEOVER|force|takeover))"
)  # TODO is lowercase accept by server?
RESETCHOICE = (
    "(?P<resetchoice>(HARD|SOFT|hard|soft))"
)  # TODO is lowercase accept by server?
COUNT = f"""(?P<count>\d+)"""
# IP re copied from:
# https://www.regular-expressions.info/ip.html
IP = """(?P<ip>(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))"""
# Port re copied from:
# https://stackoverflow.com/questions/12968093/regex-to-validate-port-number
# pompt_toolkit limit: Exception: {4}-style repetition not yet supported
PORT = "(?P<port>[1-9]|[1-5]?\d\d\d?\d?|6[1-4][0-9]\d\d\d|65[1-4]\d\d|655[1-2][0-9]|6553[1-5])"


REDIS_COMMANDS = f"""
(\s*  (?P<command_slots>({t['command_slots']}))        \s+ {SLOTS}                                    \s*)|
(\s*  (?P<command_node>({t['command_node']}))          \s+ {NODE}                                     \s*)|
(\s*  (?P<command_slot>({t['command_slot']}))          \s+ {SLOT}                                     \s*)|
(\s*  (?P<command_failoverchoice>({t['command_failoverchoice']}))  \s+ {FAILOVERCHOICE}               \s*)|
(\s*  (?P<command_resetchoice>({t['command_resetchoice']}))        \s+ {RESETCHOICE}               \s*)|
(\s*  (?P<command_slot_count>({t['command_slot_count']}))          \s+ {SLOT}   \s+   {COUNT}         \s*)|
(\s*  (?P<command>({t['command']}))                                                                   \s*)|
(\s*  (?P<command_key>({t['command_key']}))            \s+ {KEY}                                      \s*)|
(\s*  (?P<command_ip_port>({t['command_ip_port']}))    \s+ {IP}    \s+ {PORT}                         \s*)|


(\s*  (?P<command_key>(HGETALL|GET))      \s+  {KEY}                                    \s*)|
(\s*  (?P<command_key_fields>(HDEL))      \s+  {KEY}  \s+ {FIELDS}                      \s*)|
(\s*  (?P<command_key_value>(SET|KSET|HAAA))   \s+   {KEY}   \s+   {VALUE}                \s*) 
"""

redis_grammar = compile(REDIS_COMMANDS)
