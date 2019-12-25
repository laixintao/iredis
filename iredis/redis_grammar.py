"""
command_nodex: x means node?
"""
import logging

from .commands_csv_loader import group2command_res as t

logger = logging.getLogger(__name__)
CONST = {
    "failoverchoice": "TAKEOVER FORCE",
    "withscores": "WITHSCORES",
    "limit": "LIMIT",
    "expiration": "EX PX",
    "condition": "NX XX",
    "operation": "AND OR XOR NOT",
    "changed": "CH",
    "incr": "INCR",
    "resetchoice": "HARD SOFT",
    "match": "MATCH",
    "count_const": "COUNT",
    "const_store": "STORE",
    "const_storedist": "STOREDIST",
    "type_const": "TYPE",
    "type": "string list set zset hash stream",
    "position_choice": "BEFORE AFTER",
    "error": "TIMEOUT ERROR",
    "async": "ASYNC",
    "conntype": "NORMAL MASTER REPLICA PUBSUB",
    "samples": "SAMPLES",
    "slotsubcmd": "IMPORTING MIGRATING NODE STABLE",
    "weights_const": "WEIGHTS",
    "aggregate_const": "AGGREGATE",
    "aggregate": "SUM MIN MAX",
    "slowlogsub": "LEN RESET GET",
    "shutdown": "SAVE NOSAVE",
    "switch": "ON OFF SKIP",
    "const_id": "ID",
    "addr": "ADDR",
    "skipme": "SKIPME",
    "yes": "YES NO",
    "migratechoice": "COPY REPLACE",
    "auth": "AUTH",
    "const_keys": "KEYS",
    "object": "REFCOUNT ENCODING IDLETIME FREQ HELP",
    "subrestore": "REPLACE ABSTTL IDLETIME FREQ",
    "distunit": "m km ft mi",
    "geochoice": "WITHCOORD WITHDIST WITHHASH",
    "order": "ASC DESC",
}


def c(const_name):
    const_values = CONST[const_name].split()
    uppers = [x.lower() for x in const_values]
    const_values.extend(uppers)
    return "|".join(const_values)


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
LONGITUDE = fr"(?P<longitude>{_FLOAT})"
LATITUDE = fr"(?P<latitude>{_FLOAT})"
CURSOR = fr"(?P<cursor>{NUM})"
PARAMETER = fr"(?P<parameter>{VALID_TOKEN})"
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
CLIENTID = fr"(?P<clientid>{NUM})"
SECOND = fr"(?P<second>{NUM})"
TIMESTAMP = fr"(?P<timestamp>{NUM})"
PATTERN = fr"(?P<pattern>{VALID_TOKEN})"
COMMANDNAME = fr"(?P<commandname>[\w -]+)"
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
IP_PORT = fr"(?P<ip_port>{IP}:{PORT})"
HOST = fr"(?P<host>{VALID_TOKEN})"

# const choices
FAILOVERCHOICE = fr"(?P<failoverchoice>{c('failoverchoice')})"
WITHSCORES = fr"(?P<withscores>{c('withscores')})"
LIMIT = fr"(?P<limit>{c('limit')})"
EXPIRATION = fr"(?P<expiration>{c('expiration')})"
CONDITION = fr"(?P<condition>{c('condition')})"
OPERATION = fr"(?P<operation>{c('operation')})"
CHANGED = fr"(?P<changed>{c('changed')})"
INCR = fr"(?P<incr>{c('incr')})"
RESETCHOICE = fr"(?P<resetchoice>{c('resetchoice')})"
MATCH = fr"(?P<match>{c('match')})"
COUNT_CONST = fr"(?P<count_const>{c('count_const')})"
TYPE_CONST = fr"(?P<type_const>{c('type_const')})"
TYPE = fr"(?P<type>{c('type')})"
POSITION_CHOICE = fr"(?P<position_choice>{c('position_choice')})"
ERROR = fr"(?P<error>{c('error')})"
ASYNC = fr"(?P<async>{c('async')})"
CONNTYPE = fr"(?P<conntype>{c('conntype')})"
SAMPLES = fr"(?P<samples>{c('samples')})"
SLOTSUBCMD = fr"(?P<slotsubcmd>{c('slotsubcmd')})"
WEIGHTS_CONST = fr"(?P<weights_const>{c('weights_const')})"
AGGREGATE_CONST = fr"(?P<aggregate_const>{c('aggregate_const')})"
AGGREGATE = fr"(?P<aggregate>{c('aggregate')})"
SLOWLOGSUB = fr"(?P<slowlogsub>{c('slowlogsub')})"
SHUTDOWN = fr"(?P<shutdown>{c('shutdown')})"
SWITCH = fr"(?P<switch>{c('switch')})"
CONST_ID = fr"(?P<const_id>{c('const_id')})"
ADDR = fr"(?P<addr>{c('addr')})"
SKIPME = fr"(?P<skipme>{c('skipme')})"
YES = fr"(?P<yes>{c('yes')})"
MIGRATECHOICE = fr"(?P<migratechoice>{c('migratechoice')})"
AUTH = fr"(?P<auth>{c('auth')})"
CONST_KEYS = fr"(?P<const_keys>{c('const_keys')})"
OBJECT = fr"(?P<object>{c('object')})"
SUBRESTORE = fr"(?P<subrestore>{c('subrestore')})"
DISTUNIT = fr"(?P<distunit>{c('distunit')})"
GEOCHOICE = fr"(?P<geochoice>{c('geochoice')})"
ORDER = fr"(?P<order>{c('order')})"
CONST_STORE = fr"(?P<const_store>{c('const_store')})"
CONST_STOREDIST = fr"(?P<const_storedist>{c('const_storedist')})"


REDIS_COMMANDS = fr"""
(\s*  (?P<command_commandname>({t['command_commandname']}))        \s+ {COMMANDNAME}                  \s*)|
(\s*  (?P<command_slots>({t['command_slots']}))        \s+ {SLOTS}                                    \s*)|
(\s*  (?P<command_node>({t['command_node']}))          \s+ {NODE}                                     \s*)|
(\s*  (?P<command_slot>({t['command_slot']}))          \s+ {SLOT}                                     \s*)|
(\s*  (?P<command_failoverchoice>({t['command_failoverchoice']}))
                                                       \s+ {FAILOVERCHOICE}                           \s*)|
(\s*  (?P<command_resetchoice>({t['command_resetchoice']}))
                                                       \s+ {RESETCHOICE}                              \s*)|
(\s*  (?P<command_slot_count>({t['command_slot_count']}))   \s+ {SLOT}  \s+ {COUNT}                   \s*)|
(\s*  (?P<command_key_samples_count>({t['command_key_samples_count']}))
    \s+ {KEY}  \s+ {SAMPLES}  \s+ {COUNT}                                                             \s*)|
(\s*  (?P<command>({t['command']}))                                                                   \s*)|
(\s*  (?P<command_ip_port>({t['command_ip_port']}))    \s+ {IP}      \s+ {PORT}                       \s*)|
(\s*  (?P<command_epoch>({t['command_epoch']}))        \s+ {EPOCH}                                    \s*)|
(\s*  (?P<command_asyncx>({t['command_asyncx']}))      (\s+ {ASYNC})?                                 \s*)|
(\s*  (?P<command_slot_slotsubcmd_nodex>({t['command_slot_slotsubcmd_nodex']}))
                                                       \s+ {SLOT}    \s+ {SLOTSUBCMD}   (\s+ {NODE})? \s*)|
(\s*  (?P<command_password>({t['command_password']}))  \s+ {PASSWORD}                                 \s*)|
(\s*  (?P<command_message>({t['command_message']}))    \s+ {MESSAGE}                                  \s*)|
(\s*  (?P<command_messagex>({t['command_messagex']}))  (\s+{MESSAGE})?                                \s*)|
(\s*  (?P<command_index>({t['command_index']}))        \s+ {INDEX}                                    \s*)|
(\s*  (?P<command_index_index>({t['command_index_index']}))  \s+ {INDEX}  \s+ {INDEX}                 \s*)|
(\s*  (?P<command_type_conntype_x>({t['command_type_conntype_x']}))
    (\s+ {TYPE_CONST}  \s+ {CONNTYPE})?                                                               \s*)|
(\s*  (?P<command_clientid_errorx>({t['command_clientid_errorx']}))  \s+ {CLIENTID}  (\s+ {ERROR})?   \s*)|
(\s*  (?P<command_key>({t['command_key']}))            \s+ {KEY}                                      \s*)|
(\s*  (?P<command_keys>({t['command_keys']}))          \s+ {KEYS}                                     \s*)|
(\s*  (?P<command_key_value>({t['command_key_value']}))   \s+ {KEY}  \s+ {VALUE}                      \s*)|
(\s*  (?P<command_parameter_value>({t['command_parameter_value']}))   \s+ {PARAMETER}  \s+ {VALUE}    \s*)|
(\s*  (?P<command_parameter>({t['command_parameter']}))   \s+ {PARAMETER}  \s+ {VALUE}    \s*)|
(\s*  (?P<command_value>({t['command_value']}))   \s+ {VALUE}                                         \s*)|
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
(\s*  (?P<command_newkey_keys>({t['command_newkey_keys']}))  \s+ {NEWKEY}  \s+ {KEYS}                 \s*)|
(\s*  (?P<command_key_newkey_timeout>({t['command_key_newkey_timeout']}))
      \s+ {KEY}  \s+ {NEWKEY}  \s+ {TIMEOUT}                                                          \s*)|
(\s*  (?P<command_keys_timeout>({t['command_keys_timeout']}))  \s+ {KEYS}  \s+ {TIMEOUT}              \s*)|
(\s*  (?P<command_count_timeout>({t['command_count_timeout']}))  \s+ {COUNT}  \s+ {TIMEOUT}           \s*)|
(\s*  (?P<command_timeout>({t['command_timeout']}))   \s+ {TIMEOUT}                                   \s*)|
(\s*  (?P<command_key_positionchoice_pivot_value>({t['command_key_positionchoice_pivot_value']}))
      \s+ {KEY}  \s+ {POSITION_CHOICE}  \s+ {VALUE}  \s+ {VALUE}                                      \s*)|
(\s*  (?P<command_pass>({t['command_pass']}))          \s+ {ANY}                                      \s*)|
(\s*  (?P<command_any>({t['command_any']}))          \s+ {ANY}                                      \s*)|
(\s*  (?P<command_key_value_expiration_condition>({t['command_key_value_expiration_condition']}))
                                                       \s+ {KEY}     \s+ {VALUE}
                                                       (\s+ {EXPIRATION} \s+ {MILLISECOND})?
                                                       (\s+ {CONDITION})?                             \s*)|
(\s*  (?P<command_key_start_end_x>({t['command_key_start_end_x']}))
                                                       \s+ {KEY}     (\s+ {START} \s+ {END})?         \s*)|
(\s*  (?P<command_key_start_end>({t['command_key_start_end']}))
                                                       \s+ {KEY}     \s+ {START}  \s+ {END}           \s*)|
(\s*  (?P<command_key_delta>({t['command_key_delta']}))
                                                       \s+ {KEY}     \s+ {DELTA}                      \s*)|
(\s*  (?P<command_key_offset_value>({t['command_key_offset_value']}))
                                                       \s+ {KEY}     \s+ {OFFSET} \s+ {VALUE}         \s*)|
(\s*  (?P<command_key_field_value>({t['command_key_field_value']}))
                                                       \s+ {KEY}     (\s+ {FIELD} \s+ {VALUE})+       \s*)|
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
(\s*  (?P<command_geodist>({t['command_geodist']}))
      \s+ {KEY}    \s+ {MEMBER} \s+ {MEMBER} (\s+ {DISTUNIT})?                                        \s*)|
(\s*  (?P<command_key_longitude_latitude_members>({t['command_key_longitude_latitude_members']}))
      \s+ {KEY}    (\s+ {LONGITUDE} \s+ {LATITUDE} \s {MEMBER})+                                      \s*)|
(\s*  (?P<command_destination_keys>({t['command_destination_keys']}))
                                                       \s+ {DESTINATION}    \s+ {KEYS}                \s*)|
(\s*  (?P<command_object_key>({t['command_object_key']}))
                                                       \s+ {OBJECT}    \s+ {KEY}                      \s*)|
(\s*  (?P<command_key_member>({t['command_key_member']}))
                                                       \s+ {KEY}    \s+ {MEMBER}                      \s*)|
(\s*  (?P<command_key_newkey_member>({t['command_key_newkey_member']}))
                                                       \s+ {KEY}    \s+ {NEWKEY}   \s+ {MEMBER}       \s*)|
(\s*  (?P<command_key_count_x>({t['command_key_count_x']}))
                                                       \s+ {KEY}    (\s+ {COUNT})?                    \s*)|
(\s*  (?P<command_key_min_max>({t['command_key_min_max']}))
                                                       \s+ {KEY}    \s+ {MIN}      \s+ {MAX}          \s*)|
(\s*  (?P<command_key_condition_changed_incr_score_members>
    ({t['command_key_condition_changed_incr_score_members']}))  \s+ {KEY}  (\s+ {CONDITION})?
    (\s+ {CHANGED})?  (\s+ {INCR})?  (\s+ {SCORE}   \s+ {MEMBER})+                                    \s*)|
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
(\s*  (?P<command_slowlog>({t['command_slowlog']}))  \s+ {SLOWLOGSUB} \s+ {NUM}                       \s*)|
(\s*  (?P<command_switch>({t['command_switch']}))  \s+ {SWITCH}                                       \s*)|
(\s*  (?P<command_clientkill>({t['command_clientkill']}))
    (\s+ {IP_PORT})?
    (\s+ {ADDR} \s+ {IP_PORT})?
    (\s+ {CONST_ID} \s+ {CLIENTID})?
    (\s+ {TYPE_CONST} \s+ {CONNTYPE})?
    (\s+ {SKIPME} \s+ {YES})?                                                                        \s*)|
(\s*  (?P<command_migrate>({t['command_migrate']})) \s+ {HOST} \s+  {PORT} \s+ {KEY}
    \s+ {INDEX} \s+ {TIMEOUT}
    (\s+ {MIGRATECHOICE})?
    (\s+ {AUTH} \s+ {PASSWORD})?
    (\s+ {CONST_KEYS} \s+ {KEYS})?                                                                   \s*)|
(\s*  (?P<command_radius>({t['command_radius']})) \s+ {KEY} \s+  {LONGITUDE} \s+ {LATITUDE}
    \s+ {FLOAT} \s+ {DISTUNIT}
    (\s+ {GEOCHOICE})*
    (\s+ {COUNT_CONST} \s+ {COUNT})?
    (\s+ {ORDER})?
    (\s+ {CONST_STORE} \s+ {KEY})?
    (\s+ {CONST_STOREDIST} \s+ {KEY})?  \s*)|
(\s*  (?P<command_georadiusbymember>({t['command_georadiusbymember']})) \s+ {KEY} \s+ {MEMBER}
    \s+ {FLOAT} \s+ {DISTUNIT}
    (\s+ {GEOCHOICE})*
    (\s+ {COUNT_CONST} \s+ {COUNT})?
    (\s+ {ORDER})?
    (\s+ {CONST_STORE} \s+ {KEY})?
    (\s+ {CONST_STOREDIST} \s+ {KEY})?  \s*)|
(\s*  (?P<command_restore>({t['command_restore']})) \s+ {KEY} \s+  {TIMEOUT} \s+ {VALUE}
    (\s+ {SUBRESTORE} \s+ {SECOND})?                                                                 \s*)|
(\s*  (?P<command_shutdown>({t['command_shutdown']}))  \s+ {SHUTDOWN}                                 \s*)
"""
