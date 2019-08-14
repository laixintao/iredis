"""
command_nodex: x means node?
"""
from prompt_toolkit.contrib.regular_languages.compiler import compile
from .commands_csv_loader import t

VALID_TOKEN = r"""(
("([^"]|\\")*?")     |# with quotes
([^\s"]+)             # without quotes
)"""
VALID_SLOT = r"\d+"  # TODO add range? max value:16384
VALID_NODE = r"\d+"

SLOT = fr"(?P<slot>{VALID_SLOT})"
SLOTS = fr"(?P<slots>{VALID_SLOT}(\s+{VALID_SLOT})*)"
NODE = fr"(?P<node>{VALID_NODE})"
KEY = fr"(?P<key>{VALID_TOKEN})"
VALUE = fr"(?P<value>{VALID_TOKEN})"
FIELDS = fr"(?P<fields>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
FAILOVERCHOICE = (
    r"(?P<failoverchoice>(FORCE|TAKEOVER|force|takeover))"
)  # TODO is lowercase accept by server?
RESETCHOICE = (
    r"(?P<resetchoice>(HARD|SOFT|hard|soft))"
)  # TODO is lowercase accept by server?
SLOTSUBCMD = r"(?P<slotsubcmd>(IMPORTING|MIGRATING|NODE|importing|migrating|node))"
SLOTSUBCMDBARE = r"(?P<slotsubcmd>(STABLE|stable))"
COUNT = fr"(?P<count>\d+)"
MESSAGE = fr"(?P<message>{VALID_TOKEN})"
# IP re copied from:
# https://www.regular-expressions.info/ip.html
IP = r"""(?P<ip>(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.
               (25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9]))"""
# Port re copied from:
# https://stackoverflow.com/questions/12968093/regex-to-validate-port-number
# pompt_toolkit limit: Exception: {4}-style repetition not yet supported
PORT = r"(?P<port>[1-9]|[1-5]?\d\d\d?\d?|6[1-4][0-9]\d\d\d|65[1-4]\d\d|655[1-2][0-9]|6553[1-5])"
EPOCH = r"(?P<epoch>\d+)"
PASSWORD = fr"(?P<password>{VALID_TOKEN})"
INDEX = r"(?P<index>(1[0-5]|\d))"


REDIS_COMMANDS = fr"""
(\s*  (?P<command_slots>({t['command_slots']}))        \s+ {SLOTS}                                    \s*)|
(\s*  (?P<command_node>({t['command_node']}))          \s+ {NODE}                                     \s*)|
(\s*  (?P<command_slot>({t['command_slot']}))          \s+ {SLOT}                                     \s*)|
(\s*  (?P<command_failoverchoice>({t['command_failoverchoice']}))
                                                       \s+ {FAILOVERCHOICE}                           \s*)|
(\s*  (?P<command_resetchoice>({t['command_resetchoice']}))
                                                       \s+ {RESETCHOICE}                              \s*)|
(\s*  (?P<command_slot_count>({t['command_slot_count']}))
                                                       \s+ {SLOT}    \s+ {COUNT}        \s*)|
(\s*  (?P<command>({t['command']}))                                                                   \s*)|
(\s*  (?P<command_key>({t['command_key']}))            \s+ {KEY}                                      \s*)|
(\s*  (?P<command_ip_port>({t['command_ip_port']}))    \s+ {IP}      \s+ {PORT}                       \s*)|
(\s*  (?P<command_epoch>({t['command_epoch']}))        \s+ {EPOCH}                                    \s*)|
(\s*  (?P<command_slot_slotsubcmd_nodex>({t['command_slot_slotsubcmd_nodex']}))
                                                       \s+ {SLOT}    \s+ {SLOTSUBCMD}   (\s+ {NODE})? \s*)|
(\s*  (?P<command_slot_slotsubcmd_nodex>({t['command_slot_slotsubcmd_nodex']}))
                                                       \s+ {SLOT}    \s+ {SLOTSUBCMDBARE}             \s*)|
(\s*  (?P<command_password>({t['command_password']}))  \s+ {PASSWORD}                                 \s*)|
(\s*  (?P<command_message>({t['command_message']}))    \s+ {MESSAGE}                                  \s*)|
(\s*  (?P<command_messagex>({t['command_messagex']}))  (\s+{MESSAGE})?                                \s*)|
(\s*  (?P<command_index>({t['command_index']}))        \s+ {INDEX}                                    \s*)|
(\s*  (?P<command_index_index>({t['command_index_index']}))
                                                       \s+ {INDEX}   \s+ {INDEX}                      \s*)|

"""

redis_grammar = compile(REDIS_COMMANDS)
