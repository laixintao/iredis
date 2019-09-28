"""
command_nodex: x means node?
"""
import logging

from .commands_csv_loader import group2command_res as t

logger = logging.getLogger(__name__)

VALID_TOKEN = r"""(
("([^"]|\\")*?")     |# with double quotes
('([^']|\\')*?')     |# with single quotes
([^\s"]+)            # without quotes
)"""
VALID_SLOT = r"\d+"  # TODO add range? max value:16384
VALID_NODE = r"\d+"
NUM = r"\d+"
NNUM = r"-?\+?\(?\[?(\d+|inf)"  # number cloud be negative
_FLOAT = r"-?(\d|\.|e)+"
LEXNUM = fr"(\[\w+)|(\(\w+)|(\+)|(-)"

SLOT = fr"(?P<slot>{VALID_SLOT})"
SLOTS = fr"(?P<slots>{VALID_SLOT}(\s+{VALID_SLOT})*)"
NODE = fr"(?P<node>{VALID_NODE})"
KEY = fr"(?P<key>{VALID_TOKEN})"
KEYS = fr"(?P<keys>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
DESTINATION = fr"(?P<destination>{VALID_TOKEN})"
NEWKEY = fr"(?P<newkey>{VALID_TOKEN})"
VALUE = fr"(?P<value>{VALID_TOKEN})"
VALUES = fr"(?P<values>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
FIELDS = fr"(?P<fields>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
FIELD = fr"(?P<field>{VALID_TOKEN})"
MEMBER = fr"(?P<member>{VALID_TOKEN})"
MEMBERS = fr"(?P<members>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
COUNT = fr"(?P<count>{NNUM})"
MESSAGE = fr"(?P<message>{VALID_TOKEN})"
BIT = r"(?P<bit>0|1)"
FLOAT = fr"(?P<float>{_FLOAT})"
CURSOR = fr"(?P<cursor>{NUM})"
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
EPOCH = fr"(?P<epoch>{NUM})"
PASSWORD = fr"(?P<password>{VALID_TOKEN})"
INDEX = r"(?P<index>(1[0-5]|\d))"
SECOND = fr"(?P<second>{NUM})"
TIMESTAMP = fr"(?P<timestamp>{NUM})"
PATTERN = fr"(?P<pattern>{VALID_TOKEN})"
MILLISECOND = fr"(?P<millisecond>{NUM})"
TIMESTAMPMS = fr"(?P<timestampms>{NUM})"
ANY = r"(?P<any>.*)"  # TODO deleted
START = fr"(?P<start>{NNUM})"
END = fr"(?P<end>{NNUM})"
DELTA = fr"(?P<delta>{NNUM})"
OFFSET = fr"(?P<offset>{NUM})"  # string offset, can't be negative
MIN = fr"(?P<min>{NNUM})"
MAX = fr"(?P<max>{NNUM})"
POSITION = fr"(?P<position>{NNUM})"
TIMEOUT = fr"(?P<timeout>{NUM})"
SCORE = fr"(?P<score>{_FLOAT})"
LEXMIN = fr"(?P<lexmin>{LEXNUM})"
LEXMAX = fr"(?P<lexmax>{LEXNUM})"
WEIGHTS = fr"(?P<weights>{_FLOAT}(\s+{_FLOAT})*)"

# const choices
EXPIRATION = fr"(?P<expiration>(EX|PX|ex|px)\s+{NUM})"
CONDITION = r"(?P<condition>(NX|XX|nx|xx))"
OPERATION = r"(?P<operation>(AND|OR|XOR|NOT))"
CHANGED = r"(?P<changed>(CH|ch))"
INCR = r"(?P<incr>(INCR|incr))"
WITHSCORES = r"(?P<withscores>(WITHSCORES|withscores))"
FAILOVERCHOICE = r"(?P<failoverchoice>(FORCE|TAKEOVER|force|takeover))"
RESETCHOICE = r"(?P<resetchoice>(HARD|SOFT|hard|soft))"
SLOTSUBCMD = r"(?P<slotsubcmd>(IMPORTING|MIGRATING|NODE|importing|migrating|node))"
SLOTSUBCMDBARE = r"(?P<slotsubcmd>(STABLE|stable))"
WEIGHTS_CONST = r"(?P<weights_const>(WEIGHTS|weights))"
AGGREGATE_CONST = r"(?P<aggregate_const>(AGGREGATE|aggregate))"
AGGREGATE = r"(?P<aggregate>(SUM|MIN|MAX|sum|min|max))"
LIMIT = r"(?P<limit>(LIMIT|limit))"
MATCH = r"(?P<match>(MATCH|match))"
COUNT_CONST = r"(?P<count_const>(COUNT|count))"
TYPE_CONST = r"(?P<type_const>(TYPE|type))"
TYPE = r"(?P<type>(STRING|LIST|SET|ZSET|HASH|STREAM|string|list|set|zset|hash|stream))"
POSITION_CHOICE = r"(?P<position_choice>(BEFORE|AFTER|before|after))"


REDIS_COMMANDS = fr"""
(\s*  (?P<command_slots>({t['command_slots']}))        \s+ {SLOTS}                                    \s*)|
(\s*  (?P<command_node>({t['command_node']}))          \s+ {NODE}                                     \s*)|
(\s*  (?P<command_slot>({t['command_slot']}))          \s+ {SLOT}                                     \s*)|
(\s*  (?P<command_failoverchoice>({t['command_failoverchoice']}))
                                                       \s+ {FAILOVERCHOICE}                           \s*)|
(\s*  (?P<command_resetchoice>({t['command_resetchoice']}))
                                                       \s+ {RESETCHOICE}                              \s*)|
(\s*  (?P<command_slot_count>({t['command_slot_count']}))
                                                       \s+ {SLOT}    \s+ {COUNT}                      \s*)|
(\s*  (?P<command>({t['command']}))                                                                   \s*)|
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
(\s*  (?P<command_key>({t['command_key']}))            \s+ {KEY}                                      \s*)|
(\s*  (?P<command_keys>({t['command_keys']}))          \s+ {KEYS}                                     \s*)|
(\s*  (?P<command_key_value>({t['command_key_value']}))   \s+ {KEY}  \s+ {VALUE}                      \s*)|
(\s*  (?P<command_key_second>({t['command_key_second']}))
                                                       \s+ {KEY}     \s+ {SECOND}                     \s*)|
(\s*  (?P<command_key_timestamp>({t['command_key_timestamp']}))
                                                       \s+ {KEY}     \s+ {TIMESTAMP}                  \s*)|
(\s*  (?P<command_pattern>({t['command_pattern']}))    \s+ {PATTERN}                                  \s*)|
(\s*  (?P<command_key_index>({t['command_key_index']}))
                                                       \s+ {KEY}     \s+ {INDEX}                      \s*)|
(\s*  (?P<command_key_millisecond>({t['command_key_millisecond']}))
                                                       \s+ {KEY}     \s+ {MILLISECOND}                \s*)|
(\s*  (?P<command_key_timestampms>({t['command_key_timestampms']}))
                                                       \s+ {KEY}     \s+ {TIMESTAMPMS}                \s*)|
(\s*  (?P<command_key_newkey>({t['command_key_newkey']}))  \s+ {KEY}  \s+ {NEWKEY}                    \s*)|
(\s*  (?P<command_key_newkey_timeout>({t['command_key_newkey_timeout']}))
      \s+ {KEY}  \s+ {NEWKEY}  \s+ {TIMEOUT}                                                          \s*)|
(\s*  (?P<command_keys_timeout>({t['command_keys_timeout']}))
                                                       \s+ {KEYS}    \s+ {TIMEOUT}                    \s*)|
(\s*  (?P<command_key_positionchoice_pivot_value>({t['command_key_positionchoice_pivot_value']}))
      \s+ {KEY}  \s+ {POSITION_CHOICE}  \s+ {VALUE}  \s+ {VALUE}                                      \s*)|
(\s*  (?P<command_pass>({t['command_pass']}))          \s+ {ANY}                                      \s*)|
(\s*  (?P<command_key_value_expiration_condition>({t['command_key_value_expiration_condition']}))
                                                       \s+ {KEY}     \s+ {VALUE}
                                                       (\s+ {EXPIRATION})?    (\s+ {CONDITION})?      \s*)|
(\s*  (?P<command_key_start_end_x>({t['command_key_start_end_x']}))
                                                       \s+ {KEY}     (\s+ {START} \s+ {END})?         \s*)|
(\s*  (?P<command_key_start_end>({t['command_key_start_end']}))
                                                       \s+ {KEY}     \s+ {START}  \s+ {END}           \s*)|
(\s*  (?P<command_key_delta>({t['command_key_delta']}))
                                                       \s+ {KEY}     \s+ {DELTA}                      \s*)|
(\s*  (?P<command_key_offset_value>({t['command_key_offset_value']}))
                                                       \s+ {KEY}     \s+ {OFFSET} \s+ {VALUE}         \s*)|
(\s*  (?P<command_key_field_value>({t['command_key_field_value']}))
                                                       \s+ {KEY}     \s+ {FIELD} \s+ {VALUE}         \s*)|
(\s*  (?P<command_key_offset_bit>({t['command_key_offset_bit']}))
                                                       \s+ {KEY}     \s+ {OFFSET} \s+ {BIT}           \s*)|
(\s*  (?P<command_key_offset>({t['command_key_offset']}))  \s+ {KEY}  \s+ {OFFSET}                    \s*)|
(\s*  (?P<command_key_position>({t['command_key_position']}))  \s+ {KEY}  \s+ {POSITION}              \s*)|
(\s*  (?P<command_key_position_value>({t['command_key_position_value']}))
      \s+ {KEY}  \s+ {POSITION}  \s+ {VALUE}                                                          \s*)|
(\s*  (?P<command_key_second_value>({t['command_key_second_value']}))
                                                       \s+ {KEY}     \s+ {SECOND} \s+ {VALUE}         \s*)|
(\s*  (?P<command_key_float>({t['command_key_float']}))
                                                       \s+ {KEY}     \s+ {FLOAT}                      \s*)|
(\s*  (?P<command_key_valuess>({t['command_key_valuess']}))
                                                       (\s+ {KEY}    \s+ {VALUE})+                    \s*)|
(\s*  (?P<command_key_values>({t['command_key_values']}))  \s+ {KEY}  \s+ {VALUES}                    \s*)|
(\s*  (?P<command_key_millisecond_value>({t['command_key_millisecond_value']}))
                                                       \s+ {KEY}     \s+ {MILLISECOND}   \s+ {VALUE}  \s*)|
(\s*  (?P<command_operation_key_keys>({t['command_operation_key_keys']}))
                                                       \s+ {OPERATION}     \s+ {KEY} \s+ {KEYS}       \s*)|
(\s*  (?P<command_key_bit_start_end>({t['command_key_bit_start_end']}))
                                                       \s+ {KEY}              \s+ {BIT}
                                                       (\s+ {START})?         (\s+ {END})?            \s*)|
(\s*  (?P<command_key_members>({t['command_key_members']}))
                                                       \s+ {KEY}    \s+ {MEMBERS}                     \s*)|
(\s*  (?P<command_destination_keys>({t['command_destination_keys']}))
                                                       \s+ {DESTINATION}    \s+ {KEYS}                \s*)|
(\s*  (?P<command_key_member>({t['command_key_member']}))
                                                       \s+ {KEY}    \s+ {MEMBER}                      \s*)|
(\s*  (?P<command_key_newkey_member>({t['command_key_newkey_member']}))
                                                       \s+ {KEY}    \s+ {NEWKEY}   \s+ {MEMBER}       \s*)|
(\s*  (?P<command_key_count_x>({t['command_key_count_x']}))
                                                       \s+ {KEY}    (\s+ {COUNT})?                    \s*)|
(\s*  (?P<command_key_min_max>({t['command_key_min_max']}))
                                                       \s+ {KEY}    \s+ {MIN}      \s+ {MAX}          \s*)|
(\s*  (?P<command_key_condition_changed_incr_score_members>({t['command_key_condition_changed_incr_score_members']}))
                                                       \s+ {KEY}
                                                       (\s+ {CONDITION})?
                                                       (\s+ {CHANGED})?
                                                       (\s+ {INCR})?
                                                       (\s+ {SCORE}   \s+ {MEMBER})+                  \s*)|
(\s*  (?P<command_key_float_member>({t['command_key_float_member']}))
                                                       \s+ {KEY}    \s+ {FLOAT}      \s+ {MEMBER}     \s*)|
(\s*  (?P<command_key_lexmin_lexmax>({t['command_key_lexmin_lexmax']}))
                                                       \s+ {KEY}    \s+ {LEXMIN}     \s+ {LEXMAX}     \s*)|
(\s*  (?P<command_key_start_end_withscores_x>({t['command_key_start_end_withscores_x']}))
                                                       \s+ {KEY}    \s+ {START} \s+ {END}
                                                       (\s+ {WITHSCORES})?                            \s*)|
(\s*  (?P<command_key_lexmin_lexmax_limit_offset_count>
      ({t['command_key_lexmin_lexmax_limit_offset_count']}))
      \s+ {KEY}  \s+ {LEXMIN}  \s+ {LEXMAX}
      (\s+ {LIMIT}  \s+ {OFFSET}  \s+ {COUNT})?                                                       \s*)|
(\s*  (?P<command_key_min_max_withscore_x_limit_offset_count_x>
      ({t['command_key_min_max_withscore_x_limit_offset_count_x']}))
      \s+ {KEY}  \s+ {MIN}  \s+ {MAX}  (\s+ {WITHSCORES})?
      (\s+ {LIMIT}  \s+ {OFFSET}  \s+ {COUNT})?                                                       \s*)|
(\s*  (?P<command_cursor_match_pattern_count_type>({t['command_cursor_match_pattern_count_type']}))
      \s+ {CURSOR}  (\s+ {MATCH}  \s+ {PATTERN})?
      (\s+ {COUNT_CONST} \s+ {COUNT})?  (\s+ {TYPE_CONST} \s+ {TYPE})?                                \s*)|
(\s*  (?P<command_key_cursor_match_pattern_count>({t['command_key_cursor_match_pattern_count']}))
      \s+ {KEY} \s+ {CURSOR}  (\s+ {MATCH}  \s+ {PATTERN})?  (\s+ {COUNT_CONST} \s+ {COUNT})?         \s*)|
(\s*  (?P<command_key_fields>({t['command_key_fields']}))  \s+ {KEY}  \s+ {FIELDS}                    \s*)|
(\s*  (?P<command_key_field>({t['command_key_field']}))  \s+ {KEY}  \s+ {FIELD}                       \s*)|
(\s*  (?P<command_key_field_delta>({t['command_key_field_delta']}))
      \s+ {KEY}  \s+ {FIELD}  \s+ {DELTA}                                                             \s*)|
(\s*  (?P<command_key_field_float>({t['command_key_field_float']}))
      \s+ {KEY}  \s+ {FIELD}  \s+ {FLOAT}                                                             \s*)|
(\s*  (?P<command_key_fieldvalues>({t['command_key_fieldvalues']}))  \s+ {KEY}
      (\s+ {FIELD}  \s+ {VALUE})+                                                                     \s*)|
"""


# command_destination_count_keys_weights_x_aggregate_x  can not parse with key numbers.
# (\s*  (?P<command_destination_count_keys_weights_x_aggregate_x>
# ({t['command_destination_count_keys_weights_x_aggregate_x']}))
#                                                        \s+ {DESTINATION}        \s+ {COUNT} \s+ {KEYS}
#                                                        (\s+ {WEIGHTS_CONST}     \s+ {WEIGHTS})?
#                                                        (\s+ {AGGREGATE_CONST}   \s+ {AGGREGATE})?   \s*)|
