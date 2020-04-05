"""
This module describes how to match a redis command to grammar token based on
regex.

command_nodex: x means node?
command_keys: ends with s means there can be multiple <key>
"""
import logging
from functools import lru_cache

from prompt_toolkit.contrib.regular_languages.compiler import compile
from .commands import command2syntax

logger = logging.getLogger(__name__)
CONST = {
    "failoverchoice": "TAKEOVER FORCE",
    "withscores": "WITHSCORES",
    "limit": "LIMIT",
    "expiration": "EX PX",
    "condition": "NX XX",
    "keepttl": "KEEPTTL",
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
    "version": "VERSION",
    "graphevent": (
        "ACTIVE-DEFRAG-CYCLE "
        "AOF-FSYNC-ALWAYS "
        "AOF-STAT "
        "AOF-REWRITE-DIFF-WRITE "
        "AOF-RENAME "
        "AOF-WRITE "
        "AOF-WRITE-ACTIVE-CHILD "
        "AOF-WRITE-ALONE "
        "AOF-WRITE-PENDING-FSYNC "
        "COMMAND "
        "EXPIRE-CYCLE "
        "EVICTION-CYCLE "
        "EVICTION-DEL "
        "FAST-COMMAND "
        "FORK "
        "RDB-UNLINK-TEMP-FILE"
    ),
    "section": (
        "SERVER "
        "CLIENTS "
        "MEMORY "
        "PERSISTENCE "
        "STATS "
        "REPLICATION "
        "CPU "
        "COMMANDSTATS "
        "CLUSTER "
        "KEYSPACE "
        "ALL "
        "DEFAULT "
    ),
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
VERSION_NUM = fr"(?P<version_num>{NUM})"
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
REPLICATIONID = fr"(?P<replicationid>{VALID_TOKEN})"
INDEX = r"(?P<index>(1[0-5]|\d))"
CLIENTID = fr"(?P<clientid>{NUM})"
SECOND = fr"(?P<second>{NUM})"
TIMESTAMP = fr"(?P<timestamp>{NUM})"
# TODO test lexer & completer for multi spaces in command
# For now, redis command can have one space at most
COMMAND = "(\s*  (?P<command>[\w -]+))"
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
KEEPTTL = fr"(?P<keepttl>{c('keepttl')})"
GRAPHEVENT = fr"(?P<graphevent>{c('graphevent')})"
VERSION = fr"(?P<version>{c('version')})"
SECTION = fr"(?P<section>{c('section')})"

command_grammar = compile(COMMAND)

# Here are the core grammars, those are tokens after ``command``.
# E.g. SET command's syntax is "SET key value"
# Then it's grammar here is r"\s+ key \s+ value \s*", we needn't add `command`
# here because every syntaxes starts with `command` so we will prepend `command`
# in get_command_grammar function.
NEW_GRAMMAR = {
    "command_key": fr"\s+ {KEY} \s*",
    "command_pattern": fr"\s+ {PATTERN} \s*",
    "command_georadiusbymember": fr"""
        \s+ {KEY} \s+ {MEMBER}
        \s+ {FLOAT} \s+ {DISTUNIT}
        (\s+ {GEOCHOICE})*
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {ORDER})?
        (\s+ {CONST_STORE} \s+ {KEY})?
        (\s+ {CONST_STOREDIST} \s+ {KEY})? \s*""",
    "command_command": fr"\s+ {COMMAND} \s*",
    "command_slots": fr"\s+ {SLOTS} \s*",
    "command_node": fr"\s+ {NODE} \s*",
    "command_slot": fr"\s+ {SLOT} \s*",
    "command_failoverchoice": fr"\s+ {FAILOVERCHOICE} \s*",
    "command_resetchoice": fr"\s+ {RESETCHOICE} \s*",
    "command_slot_count": fr"\s+ {SLOT} \s+ {COUNT} \s*",
    "command_key_samples_count": fr"""
        \s+ {KEY} \s+ {SAMPLES} \s+ {COUNT} \s*""",
    "command": fr"\s*",
    "command_ip_port": fr"\s+ {IP} \s+ {PORT} \s*",
    "command_epoch": fr"\s+ {EPOCH} \s*",
    "command_sectionx": fr"(\s+ {SECTION})? \s*",
    "command_asyncx": fr"(\s+ {ASYNC})? \s*",
    "command_slot_slotsubcmd_nodex": fr"""
        \s+ {SLOT} \s+ {SLOTSUBCMD} (\s+ {NODE})? \s*""",
    "command_password": fr"\s+ {PASSWORD} \s*",
    "command_message": fr"\s+ {MESSAGE} \s*",
    "command_messagex": fr"(\s+{MESSAGE})? \s*",
    "command_index": fr"\s+ {INDEX} \s*",
    "command_index_index": fr"\s+ {INDEX} \s+ {INDEX} \s*",
    "command_type_conntype_x": fr"""
        (\s+ {TYPE_CONST} \s+ {CONNTYPE})? \s*""",
    "command_clientid_errorx": fr"\s+ {CLIENTID} (\s+ {ERROR})? \s*",
    "command_keys": fr"\s+ {KEYS} \s*",
    "command_key_value": fr"\s+ {KEY} \s+ {VALUE} \s*",
    "command_parameter_value": fr"\s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_parameter": fr"\s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_value": fr"\s+ {VALUE} \s*",
    "command_key_second": fr"\s+ {KEY} \s+ {SECOND} \s*",
    "command_key_timestamp": fr"\s+ {KEY} \s+ {TIMESTAMP} \s*",
    "command_key_index": fr"\s+ {KEY} \s+ {INDEX} \s*",
    "command_key_millisecond": fr"\s+ {KEY} \s+ {MILLISECOND} \s*",
    "command_key_timestampms": fr"\s+ {KEY} \s+ {TIMESTAMPMS} \s*",
    "command_key_newkey": fr"\s+ {KEY} \s+ {NEWKEY} \s*",
    "command_newkey_keys": fr"\s+ {NEWKEY} \s+ {KEYS} \s*",
    "command_key_newkey_timeout": fr"\s+ {KEY} \s+ {NEWKEY} \s+ {TIMEOUT} \s*",
    "command_keys_timeout": fr"\s+ {KEYS} \s+ {TIMEOUT} \s*",
    "command_count_timeout": fr"\s+ {COUNT} \s+ {TIMEOUT} \s*",
    "command_timeout": fr"\s+ {TIMEOUT} \s*",
    "command_key_positionchoice_pivot_value": fr"""
        \s+ {KEY} \s+ {POSITION_CHOICE} \s+ {VALUE} \s+ {VALUE} \s*""",
    "command_pass": fr"\s+ {ANY} \s*",
    "command_any": fr"\s+ {ANY} \s*",
    "command_set": fr"""
        \s+ {KEY} \s+ {VALUE}
        (
            (\s+ {EXPIRATION} \s+ {MILLISECOND})|
            (\s+ {CONDITION})|
            (\s+ {KEEPTTL})
        )*
        \s*""",
    "command_key_start_end_x": fr"\s+ {KEY} (\s+ {START} \s+ {END})? \s*",
    "command_key_start_end": fr"\s+ {KEY} \s+ {START} \s+ {END} \s*",
    "command_key_delta": fr"\s+ {KEY} \s+ {DELTA} \s*",
    "command_key_offset_value": fr"\s+ {KEY} \s+ {OFFSET} \s+ {VALUE} \s*",
    "command_key_field_value": fr"\s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_key_offset_bit": fr"\s+ {KEY} \s+ {OFFSET} \s+ {BIT} \s*",
    "command_key_offset": fr"\s+ {KEY} \s+ {OFFSET} \s*",
    "command_key_position": fr"\s+ {KEY} \s+ {POSITION} \s*",
    "command_key_position_value": fr"\s+ {KEY} \s+ {POSITION} \s+ {VALUE} \s*",
    "command_key_second_value": fr"\s+ {KEY} \s+ {SECOND} \s+ {VALUE} \s*",
    "command_key_float": fr"\s+ {KEY} \s+ {FLOAT} \s*",
    "command_key_valuess": fr"(\s+ {KEY} \s+ {VALUE})+ \s*",
    "command_key_values": fr"\s+ {KEY} \s+ {VALUES} \s*",
    "command_key_millisecond_value": fr"\s+ {KEY} \s+ {MILLISECOND} \s+ {VALUE} \s*",
    "command_operation_key_keys": fr"\s+ {OPERATION} \s+ {KEY} \s+ {KEYS} \s*",
    "command_key_bit_start_end": fr"\s+ {KEY} \s+ {BIT} (\s+ {START})? (\s+ {END})? \s*",
    "command_key_members": fr"\s+ {KEY} \s+ {MEMBERS} \s*",
    "command_geodist": fr"\s+ {KEY} \s+ {MEMBER} \s+ {MEMBER} (\s+ {DISTUNIT})? \s*",
    "command_key_longitude_latitude_members": fr"""
        \s+ {KEY} (\s+ {LONGITUDE} \s+ {LATITUDE} \s {MEMBER})+ \s*""",
    "command_destination_keys": fr"\s+ {DESTINATION} \s+ {KEYS} \s*",
    "command_object_key": fr"\s+ {OBJECT} \s+ {KEY} \s*",
    "command_key_member": fr"\s+ {KEY} \s+ {MEMBER} \s*",
    "command_key_newkey_member": fr"\s+ {KEY} \s+ {NEWKEY} \s+ {MEMBER} \s*",
    "command_key_count_x": fr"\s+ {KEY} (\s+ {COUNT})? \s*",
    "command_key_min_max": fr"\s+ {KEY} \s+ {MIN} \s+ {MAX} \s*",
    "command_key_condition_changed_incr_score_members": fr"""
        \s+ {KEY} (\s+ {CONDITION})?
        (\s+ {CHANGED})?
        (\s+ {INCR})?
        (\s+ {SCORE} \s+ {MEMBER})+ \s*""",
    "command_key_float_member": fr"\s+ {KEY} \s+ {FLOAT} \s+ {MEMBER} \s*",
    "command_key_lexmin_lexmax": fr"\s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX} \s*",
    "command_key_start_end_withscores_x": fr"""
        \s+ {KEY} \s+ {START} \s+ {END} (\s+ {WITHSCORES})? \s*""",
    "command_key_lexmin_lexmax_limit_offset_count": fr"""
        \s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX}
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_key_min_max_withscore_x_limit_offset_count_x": fr"""
        \s+ {KEY} \s+ {MIN} \s+ {MAX} (\s+ {WITHSCORES})?
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_cursor_match_pattern_count_type": fr"""
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})?
        (\s+ {COUNT_CONST} \s+ {COUNT})? (\s+ {TYPE_CONST} \s+ {TYPE})? \s*""",
    "command_key_cursor_match_pattern_count": fr"""\s+ {KEY}
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})? (\s+ {COUNT_CONST} \s+ {COUNT})? \s*""",
    "command_key_fields": fr"\s+ {KEY} \s+ {FIELDS} \s*",
    "command_key_field": fr"\s+ {KEY} \s+ {FIELD} \s*",
    "command_key_field_delta": fr"\s+ {KEY} \s+ {FIELD} \s+ {DELTA} \s*",
    "command_key_field_float": fr"\s+ {KEY} \s+ {FIELD} \s+ {FLOAT} \s*",
    "command_key_fieldvalues": fr"\s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_slowlog": fr"\s+ {SLOWLOGSUB} \s+ {NUM} \s*",
    "command_switch": fr"\s+ {SWITCH} \s*",
    "command_clientkill": fr"""
        (
            (\s+ {IP_PORT})|
            (\s+ {ADDR} \s+ {IP_PORT})|
            (\s+ {CONST_ID} \s+ {CLIENTID})|
            (\s+ {TYPE_CONST} \s+ {CONNTYPE})|
            (\s+ {SKIPME} \s+ {YES})
        )+ \s*""",
    "command_migrate": fr"""\s+ {HOST} \s+ {PORT}
        \s+ {KEY} \s+ {INDEX} \s+ {TIMEOUT} (\s+ {MIGRATECHOICE})?
        (\s+ {AUTH} \s+ {PASSWORD})? (\s+ {CONST_KEYS} \s+ {KEYS})? \s*""",
    "command_radius": fr"""\s+ {KEY}
        \s+ {LONGITUDE} \s+ {LATITUDE} \s+ {FLOAT} \s+ {DISTUNIT}
        (\s+ {GEOCHOICE})* (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {ORDER})?
        (\s+ {CONST_STORE} \s+ {KEY})?
        (\s+ {CONST_STOREDIST} \s+ {KEY})? \s*""",
    "command_restore": fr"""\s+ {KEY}
        \s+ {TIMEOUT} \s+ {VALUE} (\s+ {SUBRESTORE} \s+ {SECOND})? \s*""",
    "command_pubsubcmd_channels": fr"\s+ {PUBSUBCMD} (\s+ {CHANNEL})+ \s*",
    "command_channel_message": fr"\s+ {CHANNEL} \s+ {MESSAGE} \s*",
    "command_channels": fr"(\s+ {CHANNEL})+ \s*",
    "command_lua_any": fr"""(\s+"{DOUBLE_LUA}")? (\s+'{SINGLE_LUA}')? \s+ {ANY} \s*""",
    "command_scriptdebug": fr"\s+ {SCRIPTDEBUG} \s*",
    "command_shutdown": fr"\s+ {SHUTDOWN} \s*",
    "command_key_start_end_countx": fr"""\s+ {KEY}
        \s+ {STREAM_ID}
        \s+ {STREAM_ID}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        \s*""",
    "command_xgroup": fr"""
        (
            (\s+ {STREAM_CREATE} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_SETID} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_DESTROY} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_DELCONSUMER} \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER})
        )
        \s*""",
    "command_key_group_ids": fr"""
        \s+ {KEY} \s+ {GROUP} (\s+ {STREAM_ID})+ \s*""",
    "command_key_ids": fr"""
        \s+ {KEY} (\s+ {STREAM_ID})+ \s*""",
    "command_xinfo": fr"""
        (
            (\s+ {STREAM_CONSUMERS} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_GROUPS} \s+ {KEY})|
            (\s+ {STREAM} \s+ {KEY})|
            (\s+ {HELP})
        )
        \s*""",
    "command_xpending": fr"""
        \s+ {KEY} \s+ {GROUP}
        (\s+ {STREAM_ID} \s+ {STREAM_ID} \s+ {COUNT})?
        (\s+ {CONSUMER})?
        \s*""",
    "command_xadd": fr"""
        \s+ {KEY}
        (\s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT})?
        \s+ {STREAM_ID}
        (\s+ {SFIELD} \s+ {SVALUE})+ \s*""",
    "command_key_maxlen": fr"""
        \s+ {KEY} \s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT}
        \s*""",
    "command_xclaim": fr"""
        \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER} \s+ {MILLISECOND}
        (\s+ {STREAM_ID})+
        (\s+ {IDEL} \s+ {MILLISECOND})?
        (\s+ {TIME} \s+ {TIMESTAMP})?
        (\s+ {RETRYCOUNT} \s+ {COUNT})?
        (\s+ {FORCE})?
        (\s+ {JUSTID})?
        \s*""",
    "command_xread": fr"""
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_xreadgroup": fr"""
        \s+ {STREAM_GROUP} \s+ {GROUP} \s+ {CONSUMER}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        (\s+ {NOACK})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_bitfield": fr"""
        \s+ {KEY}
        (
            (\s+ {GET} \s+ {INTTYPE} \s+ {SHARP_OFFSET})|
            (\s+ {SET} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {INCRBY} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {OVERFLOW} \s+ {OVERFLOW_OPTION})
        )+
        \s*""",
    "command_replicationid_offset": fr"\s+ {REPLICATIONID} \s+ {OFFSET} \s*",
    "command_graphevent": fr"\s+ {GRAPHEVENT} \s*",
    "command_graphevents": fr"(\s+ {GRAPHEVENT})* \s*",
    # before redis 5: lolwut 5 1
    # start from redis 6: lolwut VERSION 5 1
    "command_version": fr"(\s+ {VERSION} \s+ {VERSION_NUM})? (\s+ {ANY})? \s*",
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

    # If a command is not supported yet, (e.g. command from latest version added
    # by Redis recently, or command from third Redis module.) return a defualt
    # grammar, so the lexer and completion won't be activated.
    if syntax is None:
        return command_grammar
    # prepend command token for this syntax
    command_allow_multi_spaces = command.replace(r" ", r"\s+")
    syntax = fr"\s* (?P<command>{command_allow_multi_spaces}) " + syntax
    # allow user input pipeline to redirect to shell, like `get json | jq .`
    syntax += pipeline

    logger.info(f"syxtax: {syntax}")

    return compile(syntax)
