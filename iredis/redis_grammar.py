"""
This module describes how to match a redis command to grammar token based on
regex.

command_nodex: x means node?
command_keys: ends with s means there can be multiple <key>
"""
import logging
from functools import lru_cache

from prompt_toolkit.contrib.regular_languages.compiler import compile
from .commands_csv_loader import command2syntax

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
    "pubsubcmd": "CHANNELS NUMSUB NUMPAT",
    "scriptdebug": "YES NO SYNC",
    "help": "HELP",
    "stream": "STREAM",
    "streams": "STREAMS",
    "stream_create": "CREATE",
    "stream_setid": "SETID",
    "stream_destroy": "DESTROY",
    "stream_delconsumer": "DELCONSUMER",
    "stream_consumers": "CONSUMERS",
    "stream_groups": "GROUPS",
    "stream_group": "GROUP",
    "maxlen": "MAXLEN",
    "idel": "IDEL",
    "time": "TIME",
    "retrycount": "RETRYCOUNT",
    "force": "FORCE",
    "justid": "JUSTID",
    "block": "BLOCK",
    "noack": "NOACK",
    "get": "GET",
    "set": "SET",
    "incrby": "INCRBY",
    "overflow": "OVERFLOW",
    "overflow_option": "WRAP SAT FAIL",
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
PATTERN = fr"(?P<pattern>{VALID_TOKEN})"
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
SFIELD = fr"(?P<sfield>{VALID_TOKEN})"
SVALUE = fr"(?P<svalue>{VALID_TOKEN})"
MEMBER = fr"(?P<member>{VALID_TOKEN})"
MEMBERS = fr"(?P<members>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
COUNT = fr"(?P<count>{NNUM})"
MESSAGE = fr"(?P<message>{VALID_TOKEN})"
CHANNEL = fr"(?P<channel>{VALID_TOKEN})"
GROUP = fr"(?P<group>{VALID_TOKEN})"
CONSUMER = fr"(?P<consumer>{VALID_TOKEN})"
BIT = r"(?P<bit>0|1)"
FLOAT = fr"(?P<float>{_FLOAT})"
LONGITUDE = fr"(?P<longitude>{_FLOAT})"
LATITUDE = fr"(?P<latitude>{_FLOAT})"
CURSOR = fr"(?P<cursor>{NUM})"
PARAMETER = fr"(?P<parameter>{VALID_TOKEN})"
DOUBLE_LUA = fr'(?P<double_lua>[^"]*)'
SINGLE_LUA = fr"(?P<single_lua>[^']*)"
INTTYPE = r"(?P<inttype>(i|u)\d+)"
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
COMMANDNAME = fr"(?P<commandname>[\w -]+)"
MILLISECOND = fr"(?P<millisecond>{NUM})"
TIMESTAMPMS = fr"(?P<timestampms>{NUM})"
ANY = r"(?P<any>.*)"  # TODO deleted
START = fr"(?P<start>{NNUM})"
END = fr"(?P<end>{NNUM})"

# for stream ids, special ids include:  -, +, $, > and *
# please see:
# https://redis.io/topics/streams-intro#special-ids-in-the-streams-api
# stream id, DO NOT use r"" here, or the \+ will be two string
# NOTE: if miss the outer (), multi IDS won't work.
STREAM_ID = "(?P<stream_id>[T\d:>+*\-\$]+)"

DELTA = fr"(?P<delta>{NNUM})"
OFFSET = fr"(?P<offset>{NUM})"  # string offset, can't be negative
SHARP_OFFSET = f"(?P<offset>\#?{NUM})"  # for bitfield command
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
PUBSUBCMD = fr"(?P<pubsubcmd>{c('pubsubcmd')})"
SCRIPTDEBUG = fr"(?P<scriptdebug>{c('scriptdebug')})"
HELP = fr"(?P<help>{c('help')})"
STREAM = fr"(?P<stream>{c('stream')})"
STREAM_GROUPS = fr"(?P<stream_groups>{c('stream_groups')})"
STREAM_GROUP = fr"(?P<stream_group>{c('stream_group')})"
STREAM_CONSUMERS = fr"(?P<stream_consumers>{c('stream_consumers')})"
STREAM_CREATE = fr"(?P<stream_create>{c('stream_create')})"
STREAM_SETID = fr"(?P<stream_setid>{c('stream_setid')})"
STREAM_DESTROY = fr"(?P<stream_destroy>{c('stream_destroy')})"
STREAM_DELCONSUMER = fr"(?P<stream_delconsumer>{c('stream_delconsumer')})"
MAXLEN = fr"(?P<maxlen>{c('maxlen')})"
APPROXIMATELY = r"(?P<approximately>~)"
IDEL = fr"(?P<idel>{c('idel')})"
TIME = fr"(?P<time>{c('time')})"
RETRYCOUNT = fr"(?P<retrycount>{c('retrycount')})"
FORCE = fr"(?P<force>{c('force')})"
JUSTID = fr"(?P<justid>{c('justid')})"
BLOCK = fr"(?P<block>{c('block')})"
STREAMS = fr"(?P<streams>{c('streams')})"
NOACK = fr"(?P<noack>{c('noack')})"
GET = fr"(?P<get>{c('get')})"
SET = fr"(?P<set>{c('set')})"
INCRBY = fr"(?P<incrby>{c('incrby')})"
OVERFLOW = fr"(?P<overflow>{c('overflow')})"
OVERFLOW_OPTION = fr"(?P<overflow_option>{c('overflow_option')})"

# TODO test lexer & completer for multi spaces in command
# FIXME invalid command like "aaa bbb ccc"
# redis command can have one space at most
# FIXME inital value should be command, not blob, user can type anything...
COMMAND = "(\s*  (?P<command_pending>[\w -]+))"
command_grammar = compile(COMMAND)

# xxin is a placeholder, when compile to grammar, it will
# be replaced to user typed command
NEW_GRAMMAR = {
    "command_key": fr"\s* (?P<command>xxin) \s+ {KEY} \s*",
    "command_pattern": fr"\s* (?P<command>xxin) \s+ {PATTERN} \s*",
    "command_georadiusbymember": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {MEMBER}
        \s+ {FLOAT} \s+ {DISTUNIT}
        (\s+ {GEOCHOICE})*
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {ORDER})?
        (\s+ {CONST_STORE} \s+ {KEY})?
        (\s+ {CONST_STOREDIST} \s+ {KEY})? \s*""",
    "command_commandname": fr"\s* (?P<command>xxin) \s+ {COMMANDNAME} \s*",
    "command_slots": fr"\s* (?P<command>xxin) \s+ {SLOTS} \s*",
    "command_node": fr"\s* (?P<command>xxin) \s+ {NODE} \s*",
    "command_slot": fr"\s* (?P<command>xxin) \s+ {SLOT} \s*",
    "command_failoverchoice": fr"\s* (?P<command>xxin) \s+ {FAILOVERCHOICE} \s*",
    "command_resetchoice": fr"\s* (?P<command>xxin) \s+ {RESETCHOICE} \s*",
    "command_slot_count": fr"\s* (?P<command>xxin) \s+ {SLOT} \s+ {COUNT} \s*",
    "command_key_samples_count": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {SAMPLES} \s+ {COUNT} \s*""",
    "command": fr"\s* (?P<command>xxin) \s*",
    "command_ip_port": fr"\s* (?P<command>xxin) \s+ {IP} \s+ {PORT} \s*",
    "command_epoch": fr"\s* (?P<command>xxin) \s+ {EPOCH} \s*",
    "command_asyncx": fr"\s* (?P<command>xxin) (\s+ {ASYNC})? \s*",
    "command_slot_slotsubcmd_nodex": fr"""\s* (?P<command>xxin)
        \s+ {SLOT} \s+ {SLOTSUBCMD} (\s+ {NODE})? \s*""",
    "command_password": fr"\s* (?P<command>xxin) \s+ {PASSWORD} \s*",
    "command_message": fr"\s* (?P<command>xxin) \s+ {MESSAGE} \s*",
    "command_messagex": fr"\s* (?P<command>xxin) (\s+{MESSAGE})? \s*",
    "command_index": fr"\s* (?P<command>xxin) \s+ {INDEX} \s*",
    "command_index_index": fr"\s* (?P<command>xxin) \s+ {INDEX} \s+ {INDEX} \s*",
    "command_type_conntype_x": fr"""\s* (?P<command>xxin)
        (\s+ {TYPE_CONST} \s+ {CONNTYPE})? \s*""",
    "command_clientid_errorx": fr"\s* (?P<command>xxin) \s+ {CLIENTID} (\s+ {ERROR})? \s*",
    "command_keys": fr"\s* (?P<command>xxin) \s+ {KEYS} \s*",
    "command_key_value": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {VALUE} \s*",
    "command_parameter_value": fr"\s* (?P<command>xxin) \s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_parameter": fr"\s* (?P<command>xxin) \s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_value": fr"\s* (?P<command>xxin) \s+ {VALUE} \s*",
    "command_key_second": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {SECOND} \s*",
    "command_key_timestamp": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {TIMESTAMP} \s*",
    "command_key_index": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {INDEX} \s*",
    "command_key_millisecond": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MILLISECOND} \s*",
    "command_key_timestampms": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {TIMESTAMPMS} \s*",
    "command_key_newkey": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {NEWKEY} \s*",
    "command_newkey_keys": fr"\s* (?P<command>xxin) \s+ {NEWKEY} \s+ {KEYS} \s*",
    "command_key_newkey_timeout": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {NEWKEY} \s+ {TIMEOUT} \s*",
    "command_keys_timeout": fr"\s* (?P<command>xxin) \s+ {KEYS} \s+ {TIMEOUT} \s*",
    "command_count_timeout": fr"\s* (?P<command>xxin) \s+ {COUNT} \s+ {TIMEOUT} \s*",
    "command_timeout": fr"\s* (?P<command>xxin) \s+ {TIMEOUT} \s*",
    "command_key_positionchoice_pivot_value": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {POSITION_CHOICE} \s+ {VALUE} \s+ {VALUE} \s*""",
    "command_pass": fr"\s* (?P<command>xxin) \s+ {ANY} \s*",
    "command_any": fr"\s* (?P<command>xxin) \s+ {ANY} \s*",
    "command_key_value_expiration_condition": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {VALUE}
        (\s+ {EXPIRATION} \s+ {MILLISECOND})? (\s+ {CONDITION})? \s*""",
    "command_key_start_end_x": fr"\s* (?P<command>xxin) \s+ {KEY} (\s+ {START} \s+ {END})? \s*",
    "command_key_start_end": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {START} \s+ {END} \s*",
    "command_key_delta": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {DELTA} \s*",
    "command_key_offset_value": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {OFFSET} \s+ {VALUE} \s*",
    "command_key_field_value": fr"\s* (?P<command>xxin) \s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_key_offset_bit": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {OFFSET} \s+ {BIT} \s*",
    "command_key_offset": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {OFFSET} \s*",
    "command_key_position": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {POSITION} \s*",
    "command_key_position_value": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {POSITION} \s+ {VALUE} \s*",
    "command_key_second_value": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {SECOND} \s+ {VALUE} \s*",
    "command_key_float": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FLOAT} \s*",
    "command_key_valuess": fr"\s* (?P<command>xxin) (\s+ {KEY} \s+ {VALUE})+ \s*",
    "command_key_values": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {VALUES} \s*",
    "command_key_millisecond_value": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MILLISECOND} \s+ {VALUE} \s*",
    "command_operation_key_keys": fr"\s* (?P<command>xxin) \s+ {OPERATION} \s+ {KEY} \s+ {KEYS} \s*",
    "command_key_bit_start_end": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {BIT} (\s+ {START})? (\s+ {END})? \s*",
    "command_key_members": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MEMBERS} \s*",
    "command_geodist": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MEMBER} \s+ {MEMBER} (\s+ {DISTUNIT})? \s*",
    "command_key_longitude_latitude_members": fr"""\s* (?P<command>xxin)
        \s+ {KEY} (\s+ {LONGITUDE} \s+ {LATITUDE} \s {MEMBER})+ \s*""",
    "command_destination_keys": fr"\s* (?P<command>xxin) \s+ {DESTINATION} \s+ {KEYS} \s*",
    "command_object_key": fr"\s* (?P<command>xxin) \s+ {OBJECT} \s+ {KEY} \s*",
    "command_key_member": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MEMBER} \s*",
    "command_key_newkey_member": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {NEWKEY} \s+ {MEMBER} \s*",
    "command_key_count_x": fr"\s* (?P<command>xxin) \s+ {KEY} (\s+ {COUNT})? \s*",
    "command_key_min_max": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {MIN} \s+ {MAX} \s*",
    "command_key_condition_changed_incr_score_members": fr"""\s* (?P<command>xxin)
        \s+ {KEY} (\s+ {CONDITION})?
        (\s+ {CHANGED})?
        (\s+ {INCR})?
        (\s+ {SCORE} \s+ {MEMBER})+ \s*""",
    "command_key_float_member": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FLOAT} \s+ {MEMBER} \s*",
    "command_key_lexmin_lexmax": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX} \s*",
    "command_key_start_end_withscores_x": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {START} \s+ {END} (\s+ {WITHSCORES})? \s*""",
    "command_key_lexmin_lexmax_limit_offset_count": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX}
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_key_min_max_withscore_x_limit_offset_count_x": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {MIN} \s+ {MAX} (\s+ {WITHSCORES})?
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_cursor_match_pattern_count_type": fr"""\s* (?P<command>xxin)
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})?
        (\s+ {COUNT_CONST} \s+ {COUNT})? (\s+ {TYPE_CONST} \s+ {TYPE})? \s*""",
    "command_key_cursor_match_pattern_count": fr"""\s* (?P<command>xxin) \s+ {KEY}
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})? (\s+ {COUNT_CONST} \s+ {COUNT})? \s*""",
    "command_key_fields": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FIELDS} \s*",
    "command_key_field": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FIELD} \s*",
    "command_key_field_delta": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FIELD} \s+ {DELTA} \s*",
    "command_key_field_float": fr"\s* (?P<command>xxin) \s+ {KEY} \s+ {FIELD} \s+ {FLOAT} \s*",
    "command_key_fieldvalues": fr"\s* (?P<command>xxin) \s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_slowlog": fr"\s* (?P<command>xxin) \s+ {SLOWLOGSUB} \s+ {NUM} \s*",
    "command_switch": fr"\s* (?P<command>xxin) \s+ {SWITCH} \s*",
    "command_clientkill": fr"""\s* (?P<command>xxin) (\s+ {IP_PORT})?
        (\s+ {ADDR} \s+ {IP_PORT})?
        (\s+ {CONST_ID} \s+ {CLIENTID})?
        (\s+ {TYPE_CONST} \s+ {CONNTYPE})?
        (\s+ {SKIPME} \s+ {YES})? \s*""",
    "command_migrate": fr"""\s* (?P<command>xxin) \s+ {HOST} \s+ {PORT}
        \s+ {KEY} \s+ {INDEX} \s+ {TIMEOUT} (\s+ {MIGRATECHOICE})?
        (\s+ {AUTH} \s+ {PASSWORD})? (\s+ {CONST_KEYS} \s+ {KEYS})? \s*""",
    "command_radius": fr"""\s* (?P<command>xxin) \s+ {KEY}
        \s+ {LONGITUDE} \s+ {LATITUDE} \s+ {FLOAT} \s+ {DISTUNIT}
        (\s+ {GEOCHOICE})* (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {ORDER})?
        (\s+ {CONST_STORE} \s+ {KEY})?
        (\s+ {CONST_STOREDIST} \s+ {KEY})? \s*""",
    "command_restore": fr"""\s* (?P<command>xxin) \s+ {KEY}
        \s+ {TIMEOUT} \s+ {VALUE} (\s+ {SUBRESTORE} \s+ {SECOND})? \s*""",
    "command_pubsubcmd_channels": fr"\s* (?P<command>xxin) \s+ {PUBSUBCMD} (\s+ {CHANNEL})+ \s*",
    "command_channel_message": fr"\s* (?P<command>xxin) \s+ {CHANNEL} \s+ {MESSAGE} \s*",
    "command_channels": fr"\s* (?P<command>xxin) (\s+ {CHANNEL})+ \s*",
    "command_lua_any": fr"""\s* (?P<command>xxin) (\s+"{DOUBLE_LUA}")? (\s+'{SINGLE_LUA}')? \s+ {ANY} \s*""",
    "command_scriptdebug": fr"\s* (?P<command>xxin) \s+ {SCRIPTDEBUG} \s*",
    "command_shutdown": fr"\s* (?P<command>xxin) \s+ {SHUTDOWN} \s*",
    "command_key_start_end_countx": fr"""\s* (?P<command>xxin) \s+ {KEY}
        \s+ {STREAM_ID}
        \s+ {STREAM_ID}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        \s*""",
    "command_xgroup": fr"""\s* (?P<command>xxin)
        (
            (\s+ {STREAM_CREATE} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_SETID} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_DESTROY} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_DELCONSUMER} \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER})
        )
        \s*""",
    "command_key_group_ids": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {GROUP} (\s+ {STREAM_ID})+ \s*""",
    "command_key_ids": fr"""\s* (?P<command>xxin)
        \s+ {KEY} (\s+ {STREAM_ID})+ \s*""",
    "command_xinfo": fr"""\s* (?P<command>xxin)
        (
            (\s+ {STREAM_CONSUMERS} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_GROUPS} \s+ {KEY})|
            (\s+ {STREAM} \s+ {KEY})|
            (\s+ {HELP})
        )
        \s*""",
    "command_xpending": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {GROUP}
        (\s+ {STREAM_ID} \s+ {STREAM_ID} \s+ {COUNT})?
        (\s+ {CONSUMER})?
        \s*""",
    "command_xadd": fr"""\s* (?P<command>xxin)
        \s+ {KEY}
        (\s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT})?
        \s+ {STREAM_ID}
        (\s+ {SFIELD} \s+ {SVALUE})+ \s*""",
    "command_key_maxlen": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT}
        \s*""",
    "command_xclaim": fr"""\s* (?P<command>xxin)
        \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER} \s+ {MILLISECOND}
        (\s+ {STREAM_ID})+
        (\s+ {IDEL} \s+ {MILLISECOND})?
        (\s+ {TIME} \s+ {TIMESTAMP})?
        (\s+ {RETRYCOUNT} \s+ {COUNT})?
        (\s+ {FORCE})?
        (\s+ {JUSTID})?
        \s*""",
    "command_xread": fr"""\s* (?P<command>xxin)
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_xreadgroup": fr"""\s* (?P<command>xxin)
        \s+ {STREAM_GROUP} \s+ {GROUP} \s+ {CONSUMER}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        (\s+ {NOACK})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_bitfield": fr"""\s* (?P<command>xxin)
        \s+ {KEY}
        (
            (\s+ {GET} \s+ {INTTYPE} \s+ {SHARP_OFFSET})|
            (\s+ {SET} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {INCRBY} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {OVERFLOW} \s+ {OVERFLOW_OPTION})
        )+
        \s*""",
}

pipeline = r"(?P<shellcommand>\|.*)?"


@lru_cache(maxsize=256)
def get_command_grammar(command):
    """
    :param command: command name in upper case. This command must be raw user
        input, otherwise can't match in lexer, cause this command to be invalid;
    """
    syntax_name = command2syntax[command.upper()]
    syntax = NEW_GRAMMAR.get(syntax_name)

    # TODO this should be deleted
    if syntax is None:
        return command_grammar
    syntax = syntax.replace(r"xxin", command.replace(r" ", r"\s+"))
    syntax += pipeline

    logger.info(f"syxtax: {syntax}")

    return compile(syntax)
