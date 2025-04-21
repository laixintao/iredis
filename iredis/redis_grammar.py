# noqa: F541
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
    "withvalues_const": "WITHVALUES",
    "limit": "LIMIT",
    "expiration": "EX PX",
    "exat_const": "EXAT",
    "pxat_const": "PXAT",
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
    "async": "ASYNC SYNC",
    "conntype": "NORMAL MASTER REPLICA PUBSUB",
    "samples": "SAMPLES",
    "slotsubcmd": "IMPORTING MIGRATING NODE STABLE",
    "weights_const": "WEIGHTS",
    "aggregate_const": "AGGREGATE",
    "aggregate": "SUM MIN MAX",
    "slowlogsub": "LEN RESET GET",
    "shutdown": "SAVE NOSAVE",
    "switch": "ON OFF SKIP",
    "on_off": "ON OFF",
    "const_id": "ID",
    "addr": "ADDR",
    "laddr": "LADDR",
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
    "idle": "IDLE",
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
    "schedule": "SCHEDULE",
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
    "redirect_const": "REDIRECT",
    "prefix_const": "PREFIX",
    "bcast_const": "BCAST",
    "optin_const": "OPTIN",
    "optout_const": "OPTOUT",
    "noloop_const": "NOLOOP",
    "reset_const": "RESET",
    "const_user": "USER",
    "full_const": "FULL",
    "str_algo": "LCS",
    "len_const": "LEN",
    "idx_const": "IDX",
    "minmatchlen_const": "MINMATCHLEN",
    "withmatchlen_const": "WITHMATCHLEN",
    "strings_const": "STRINGS",
    "rank_const": "RANK",
    "lr_const": "LEFT RIGHT",
    "pause_type": "WRITE ALL",
    "db_const": "DB",
    "replace_const": "REPLACE",
    "to_const": "TO",
    "timeout_const": "TIMEOUT",
    "abort_const": "ABORT",
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
PATTERN = rf"(?P<pattern>{VALID_TOKEN})"
VALID_SLOT = r"\d+"  # TODO add range? max value:16384
VALID_NODE = r"\w+"
NUM = r"\d+"
NNUM = r"-?\+?\(?\[?(\d+|inf)"  # number cloud be negative
_FLOAT = r"-?(\d|\.|e)+"
DOUBLE = r"\d*(\.\d+)?"
LEXNUM = r"(\[\w+)|(\(\w+)|(\+)|(-)"

SLOT = rf"(?P<slot>{VALID_SLOT})"
SLOTS = rf"(?P<slots>{VALID_SLOT}(\s+{VALID_SLOT})*)"
NODE = rf"(?P<node>{VALID_NODE})"
KEY = rf"(?P<key>{VALID_TOKEN})"
KEYS = rf"(?P<keys>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
PREFIX = rf"(?P<prefix>{VALID_TOKEN})"
PREFIXES = rf"(?P<prefixes>{VALID_TOKEN}(\s+{VALID_TOKEN})*?)"
DESTINATION = rf"(?P<destination>{VALID_TOKEN})"
NEWKEY = rf"(?P<newkey>{VALID_TOKEN})"
VALUE = rf"(?P<value>{VALID_TOKEN})"
VALUES = rf"(?P<values>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
ELEMENT = rf"(?P<element>{VALID_TOKEN})"  # element for list
FIELDS = rf"(?P<fields>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
FIELD = rf"(?P<field>{VALID_TOKEN})"
SFIELD = rf"(?P<sfield>{VALID_TOKEN})"
SVALUE = rf"(?P<svalue>{VALID_TOKEN})"
MEMBER = rf"(?P<member>{VALID_TOKEN})"
MEMBERS = rf"(?P<members>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
COUNT = rf"(?P<count>{NNUM})"
LEN = rf"(?P<len>{NNUM})"
RANK = rf"(?P<rank>{NNUM})"
VERSION_NUM = rf"(?P<version_num>{NUM})"
MESSAGE = rf"(?P<message>{VALID_TOKEN})"
CHANNEL = rf"(?P<channel>{VALID_TOKEN})"
GROUP = rf"(?P<group>{VALID_TOKEN})"
CONSUMER = rf"(?P<consumer>{VALID_TOKEN})"
CATEGORYNAME = rf"(?P<categoryname>{VALID_TOKEN})"
USERNAME = rf"(?P<username>{VALID_TOKEN})"
RULE = rf"(?P<rule>{VALID_TOKEN})"
BIT = r"(?P<bit>0|1)"
FLOAT = rf"(?P<float>{_FLOAT})"
LONGITUDE = rf"(?P<longitude>{_FLOAT})"
LATITUDE = rf"(?P<latitude>{_FLOAT})"
CURSOR = rf"(?P<cursor>{NUM})"
PARAMETER = rf"(?P<parameter>{VALID_TOKEN})"
DOUBLE_LUA = r'(?P<double_lua>[^"]*)'
SINGLE_LUA = r"(?P<single_lua>[^']*)"
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
EPOCH = rf"(?P<epoch>{NUM})"
PASSWORD = rf"(?P<password>{VALID_TOKEN})"
REPLICATIONID = rf"(?P<replicationid>{VALID_TOKEN})"
INDEX = r"(?P<index>(1[0-5]|\d))"
CLIENTID = rf"(?P<clientid>{NUM})"
CLIENTIDS = rf"(?P<clientids>{NUM}(\s+{NUM})*)"

SECOND = rf"(?P<second>{NUM})"
TIMESTAMP = r"(?P<timestamp>[T\d:>+*\-\$]+)"
# TODO test lexer & completer for multi spaces in command
# For now, redis command can have one space at most
COMMAND = r"(\s*  (?P<command>[\w -]+))"
MILLISECOND = rf"(?P<millisecond>{NUM})"
TIMESTAMPMS = r"(?P<timestampms>[T\d:>+*\-\$]+)"
ANY = r"(?P<any>.*)"  # TODO deleted
START = rf"(?P<start>{NNUM})"
END = rf"(?P<end>{NNUM})"

# for stream ids, special ids include:  -, +, $, > and *
# please see:
# https://redis.io/topics/streams-intro#special-ids-in-the-streams-api
# stream id, DO NOT use r"" here, or the \+ will be two string
# NOTE: if miss the outer (), multi IDS won't work.
STREAM_ID = r"(?P<stream_id>[T\d:>+*\-\$]+)"

DELTA = rf"(?P<delta>{NNUM})"
OFFSET = rf"(?P<offset>{NUM})"  # string offset, can't be negative
SHARP_OFFSET = rf"(?P<offset>\#?{NUM})"  # for bitfield command
MIN = rf"(?P<min>{NNUM})"
MAX = rf"(?P<max>{NNUM})"
POSITION = rf"(?P<position>{NNUM})"
SCORE = rf"(?P<score>{_FLOAT})"
LEXMIN = rf"(?P<lexmin>{LEXNUM})"
LEXMAX = rf"(?P<lexmax>{LEXNUM})"
WEIGHTS = rf"(?P<weights>{_FLOAT}(\s+{_FLOAT})*)"
IP_PORT = rf"(?P<ip_port>{IP}:{PORT})"
HOST = rf"(?P<host>{VALID_TOKEN})"
MIN = rf"(?P<min>{NNUM})"
MAX = rf"(?P<max>{NNUM})"
POSITION = rf"(?P<position>{NNUM})"
TIMEOUT = rf"(?P<timeout>{DOUBLE})"
SCORE = rf"(?P<score>{_FLOAT})"
LEXMIN = rf"(?P<lexmin>{LEXNUM})"
LEXMAX = rf"(?P<lexmax>{LEXNUM})"
WEIGHTS = rf"(?P<weights>{_FLOAT}(\s+{_FLOAT})*)"
IP_PORT = rf"(?P<ip_port>{IP}:{PORT})"
HOST = rf"(?P<host>{VALID_TOKEN})"

# const choices
FAILOVERCHOICE = rf"(?P<failoverchoice>{c('failoverchoice')})"
WITHSCORES = rf"(?P<withscores>{c('withscores')})"
LIMIT = rf"(?P<limit>{c('limit')})"
EXPIRATION = rf"(?P<expiration>{c('expiration')})"
CONDITION = rf"(?P<condition>{c('condition')})"
OPERATION = rf"(?P<operation>{c('operation')})"
CHANGED = rf"(?P<changed>{c('changed')})"
INCR = rf"(?P<incr>{c('incr')})"
RESETCHOICE = rf"(?P<resetchoice>{c('resetchoice')})"
MATCH = rf"(?P<match>{c('match')})"
COUNT_CONST = rf"(?P<count_const>{c('count_const')})"
TYPE_CONST = rf"(?P<type_const>{c('type_const')})"
TYPE = rf"(?P<type>{c('type')})"
POSITION_CHOICE = rf"(?P<position_choice>{c('position_choice')})"
ERROR = rf"(?P<error>{c('error')})"
ASYNC = rf"(?P<async>{c('async')})"
CONNTYPE = rf"(?P<conntype>{c('conntype')})"
SAMPLES = rf"(?P<samples>{c('samples')})"
SLOTSUBCMD = rf"(?P<slotsubcmd>{c('slotsubcmd')})"
WEIGHTS_CONST = rf"(?P<weights_const>{c('weights_const')})"
AGGREGATE_CONST = rf"(?P<aggregate_const>{c('aggregate_const')})"
AGGREGATE = rf"(?P<aggregate>{c('aggregate')})"
SLOWLOGSUB = rf"(?P<slowlogsub>{c('slowlogsub')})"
SHUTDOWN = rf"(?P<shutdown>{c('shutdown')})"
SWITCH = rf"(?P<switch>{c('switch')})"
ON_OFF = rf"(?P<on_off>{c('on_off')})"
CONST_ID = rf"(?P<const_id>{c('const_id')})"
CONST_USER = rf"(?P<const_user>{c('const_user')})"
ADDR = rf"(?P<addr>{c('addr')})"
LADDR = rf"(?P<laddr>{c('laddr')})"
SKIPME = rf"(?P<skipme>{c('skipme')})"
YES = rf"(?P<yes>{c('yes')})"
MIGRATECHOICE = rf"(?P<migratechoice>{c('migratechoice')})"
AUTH = rf"(?P<auth>{c('auth')})"
CONST_KEYS = rf"(?P<const_keys>{c('const_keys')})"
OBJECT = rf"(?P<object>{c('object')})"
SUBRESTORE = rf"(?P<subrestore>{c('subrestore')})"
DISTUNIT = rf"(?P<distunit>{c('distunit')})"
GEOCHOICE = rf"(?P<geochoice>{c('geochoice')})"
ORDER = rf"(?P<order>{c('order')})"
CONST_STORE = rf"(?P<const_store>{c('const_store')})"
CONST_STOREDIST = rf"(?P<const_storedist>{c('const_storedist')})"
PUBSUBCMD = rf"(?P<pubsubcmd>{c('pubsubcmd')})"
SCRIPTDEBUG = rf"(?P<scriptdebug>{c('scriptdebug')})"
HELP = rf"(?P<help>{c('help')})"
STREAM = rf"(?P<stream>{c('stream')})"
STREAM_GROUPS = rf"(?P<stream_groups>{c('stream_groups')})"
STREAM_GROUP = rf"(?P<stream_group>{c('stream_group')})"
STREAM_CONSUMERS = rf"(?P<stream_consumers>{c('stream_consumers')})"
STREAM_CREATE = rf"(?P<stream_create>{c('stream_create')})"
STREAM_SETID = rf"(?P<stream_setid>{c('stream_setid')})"
STREAM_DESTROY = rf"(?P<stream_destroy>{c('stream_destroy')})"
STREAM_DELCONSUMER = rf"(?P<stream_delconsumer>{c('stream_delconsumer')})"
MAXLEN = rf"(?P<maxlen>{c('maxlen')})"
APPROXIMATELY = r"(?P<approximately>~)"
IDLE = rf"(?P<idle>{c('idle')})"
TIME = rf"(?P<time>{c('time')})"
RETRYCOUNT = rf"(?P<retrycount>{c('retrycount')})"
FORCE = rf"(?P<force>{c('force')})"
JUSTID = rf"(?P<justid>{c('justid')})"
BLOCK = rf"(?P<block>{c('block')})"
STREAMS = rf"(?P<streams>{c('streams')})"
NOACK = rf"(?P<noack>{c('noack')})"
GET = rf"(?P<get>{c('get')})"
SET = rf"(?P<set>{c('set')})"
INCRBY = rf"(?P<incrby>{c('incrby')})"
OVERFLOW = rf"(?P<overflow>{c('overflow')})"
OVERFLOW_OPTION = rf"(?P<overflow_option>{c('overflow_option')})"
KEEPTTL = rf"(?P<keepttl>{c('keepttl')})"
GRAPHEVENT = rf"(?P<graphevent>{c('graphevent')})"
VERSION = rf"(?P<version>{c('version')})"
SECTION = rf"(?P<section>{c('section')})"
SCHEDULE = rf"(?P<schedule>{c('schedule')})"

REDIRECT_CONST = rf"(?P<redirect_const>{c('redirect_const')})"
PREFIX_CONST = rf"(?P<prefix_const>{c('prefix_const')})"
BCAST_CONST = rf"(?P<bcast_const>{c('bcast_const')})"
OPTIN_CONST = rf"(?P<optin_const>{c('optin_const')})"
OPTOUT_CONST = rf"(?P<optout_const>{c('optout_const')})"
NOLOOP_CONST = rf"(?P<noloop_const>{c('noloop_const')})"

RESET_CONST = rf"(?P<reset_const>{c('reset_const')})"
FULL_CONST = rf"(?P<full_const>{c('full_const')})"

STR_ALGO = rf"(?P<str_algo>{c('str_algo')})"
LEN_CONST = rf"(?P<len_const>{c('len_const')})"
IDX_CONST = rf"(?P<idx_const>{c('idx_const')})"
MINMATCHLEN_CONST = rf"(?P<minmatchlen_const>{c('minmatchlen_const')})"
WITHMATCHLEN_CONST = rf"(?P<withmatchlen_const>{c('withmatchlen_const')})"
STRINGS_CONST = rf"(?P<strings_const>{c('strings_const')})"
RANK_CONST = rf"(?P<rank_const>{c('rank_const')})"

LR_CONST = rf"(?P<lr_const>{c('lr_const')})"
PAUSE_TYPE = rf"(?P<pause_type>{c('pause_type')})"
DB_CONST = rf"(?P<db_const>{c('db_const')})"
REPLACE_CONST = rf"(?P<replace_const>{c('replace_const')})"
TO_CONST = rf"(?P<to_const>{c('to_const')})"
TIMEOUT_CONST = rf"(?P<timeout_const>{c('timeout_const')})"
ABORT_CONST = rf"(?P<abort_const>{c('abort_const')})"
PXAT_CONST = rf"(?P<pxat_const>{c('pxat_const')})"
EXAT_CONST = rf"(?P<exat_const>{c('exat_const')})"
WITHVALUES_CONST = rf"(?P<withvalues_const>{c('withvalues_const')})"

command_grammar = compile(COMMAND)

# Here are the core grammars, those are tokens after ``command``.
# E.g. SET command's syntax is "SET key value"
# Then it's grammar here is r"\s+ key \s+ value \s*", we needn't add `command`
# here because every syntaxes starts with `command` so we will prepend `command`
# in get_command_grammar function.
GRAMMAR = {
    "command_key": rf"\s+ {KEY} \s*",
    "command_pattern": rf"\s+ {PATTERN} \s*",
    "command_command": rf"\s+ {COMMAND} \s*",
    "command_slots": rf"\s+ {SLOTS} \s*",
    "command_node": rf"\s+ {NODE} \s*",
    "command_slot": rf"\s+ {SLOT} \s*",
    "command_failoverchoice": rf"\s+ {FAILOVERCHOICE} \s*",
    "command_resetchoice": rf"\s+ {RESETCHOICE} \s*",
    "command_slot_count": rf"\s+ {SLOT} \s+ {COUNT} \s*",
    "command_key_samples_count": rf"""
        \s+ {KEY} \s+ {SAMPLES} \s+ {COUNT} \s*""",
    "command": r"\s*",
    "command_ip_port": rf"\s+ {IP} \s+ {PORT} \s*",
    "command_epoch": rf"\s+ {EPOCH} \s*",
    "command_yes": rf"\s+ {YES} \s*",
    "command_sectionx": rf"(\s+ {SECTION})? \s*",
    "command_asyncx": rf"(\s+ {ASYNC})? \s*",
    "command_slot_slotsubcmd_nodex": rf"""
        \s+ {SLOT} \s+ {SLOTSUBCMD} (\s+ {NODE})? \s*""",
    "command_password": rf"\s+ {PASSWORD} \s*",
    "command_usernamex_password": rf"(\s+ {USERNAME})? \s+ {PASSWORD} \s*",
    "command_message": rf"\s+ {MESSAGE} \s*",
    "command_messagex": rf"(\s+{MESSAGE})? \s*",
    "command_index": rf"\s+ {INDEX} \s*",
    "command_index_index": rf"\s+ {INDEX} \s+ {INDEX} \s*",
    "command_client_list": rf"""
        (
            (\s+ {TYPE_CONST} \s+ {CONNTYPE})|
            (\s+ {CONST_ID} \s+ {CLIENTIDS})
        )*
    \s*""",
    "command_clientid_errorx": rf"\s+ {CLIENTID} (\s+ {ERROR})? \s*",
    "command_keys": rf"\s+ {KEYS} \s*",
    "command_key_value": rf"\s+ {KEY} \s+ {VALUE} \s*",
    "command_parameter_value": rf"\s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_parameter": rf"\s+ {PARAMETER} \s+ {VALUE} \s*",
    "command_value": rf"\s+ {VALUE} \s*",
    "command_key_second": rf"\s+ {KEY} \s+ {SECOND} \s*",
    "command_key_timestamp": rf"\s+ {KEY} \s+ {TIMESTAMP} \s*",
    "command_key_index": rf"\s+ {KEY} \s+ {INDEX} \s*",
    "command_key_millisecond": rf"\s+ {KEY} \s+ {MILLISECOND} \s*",
    "command_key_timestampms": rf"\s+ {KEY} \s+ {TIMESTAMPMS} \s*",
    "command_key_newkey": rf"\s+ {KEY} \s+ {NEWKEY} \s*",
    "command_newkey_keys": rf"\s+ {NEWKEY} \s+ {KEYS} \s*",
    "command_key_newkey_timeout": rf"\s+ {KEY} \s+ {NEWKEY} \s+ {TIMEOUT} \s*",
    "command_keys_timeout": rf"\s+ {KEYS} \s+ {TIMEOUT} \s*",
    "command_count_timeout": rf"\s+ {COUNT} \s+ {TIMEOUT} \s*",
    "command_pause": rf"\s+ {TIMEOUT} (\s+ {PAUSE_TYPE})? \s*",
    "command_key_positionchoice_pivot_value": rf"""
        \s+ {KEY} \s+ {POSITION_CHOICE} \s+ {VALUE} \s+ {VALUE} \s*""",
    "command_pass": rf"\s+ {ANY} \s*",
    "command_any": rf"\s+ {ANY} \s*",
    "command_set": rf"""
        \s+ {KEY} \s+ {VALUE}
        (
            (\s+ {EXPIRATION} \s+ {MILLISECOND})|
            (\s+ {CONDITION})|
            (\s+ {KEEPTTL})
        )*
        \s*""",
    "command_key_start_end_x": rf"\s+ {KEY} (\s+ {START} \s+ {END})? \s*",
    "command_key_start_end": rf"\s+ {KEY} \s+ {START} \s+ {END} \s*",
    "command_key_delta": rf"\s+ {KEY} \s+ {DELTA} \s*",
    "command_key_offset_value": rf"\s+ {KEY} \s+ {OFFSET} \s+ {VALUE} \s*",
    "command_key_field_value": rf"\s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_key_offset_bit": rf"\s+ {KEY} \s+ {OFFSET} \s+ {BIT} \s*",
    "command_key_offset": rf"\s+ {KEY} \s+ {OFFSET} \s*",
    "command_key_position": rf"\s+ {KEY} \s+ {POSITION} \s*",
    "command_key_position_value": rf"\s+ {KEY} \s+ {POSITION} \s+ {VALUE} \s*",
    "command_key_second_value": rf"\s+ {KEY} \s+ {SECOND} \s+ {VALUE} \s*",
    "command_key_float": rf"\s+ {KEY} \s+ {FLOAT} \s*",
    "command_key_valuess": rf"(\s+ {KEY} \s+ {VALUE})+ \s*",
    "command_key_values": rf"\s+ {KEY} \s+ {VALUES} \s*",
    "command_key_millisecond_value": rf"\s+ {KEY} \s+ {MILLISECOND} \s+ {VALUE} \s*",
    "command_operation_key_keys": rf"\s+ {OPERATION} \s+ {KEY} \s+ {KEYS} \s*",
    "command_key_bit_start_end": rf"\s+ {KEY} \s+ {BIT} (\s+ {START})? (\s+ {END})? \s*",
    "command_key_members": rf"\s+ {KEY} \s+ {MEMBERS} \s*",
    "command_geodist": rf"\s+ {KEY} \s+ {MEMBER} \s+ {MEMBER} (\s+ {DISTUNIT})? \s*",
    "command_key_longitude_latitude_members": rf"""
        \s+ {KEY}
        (\s+ {CONDITION})?
        (\s+ {CHANGED})?
        (\s+ {LONGITUDE} \s+ {LATITUDE} \s {MEMBER})+
    \s*""",
    "command_destination_keys": rf"\s+ {DESTINATION} \s+ {KEYS} \s*",
    "command_object_key": rf"\s+ {OBJECT} \s+ {KEY} \s*",
    "command_key_member": rf"\s+ {KEY} \s+ {MEMBER} \s*",
    "command_key_any": rf"\s+ {KEY} \s+ {ANY} \s*",
    "command_key_key_any": rf"\s+ {KEY} \s+ {KEY} \s+ {ANY} \s*",
    "command_key_newkey_member": rf"\s+ {KEY} \s+ {NEWKEY} \s+ {MEMBER} \s*",
    "command_key_count_x": rf"\s+ {KEY} (\s+ {COUNT})? \s*",
    "command_key_min_max": rf"\s+ {KEY} \s+ {MIN} \s+ {MAX} \s*",
    "command_key_condition_changed_incr_score_members": rf"""
        \s+ {KEY} (\s+ {CONDITION})?
        (\s+ {CHANGED})?
        (\s+ {INCR})?
        (\s+ {SCORE} \s+ {MEMBER})+ \s*""",
    "command_key_float_member": rf"\s+ {KEY} \s+ {FLOAT} \s+ {MEMBER} \s*",
    "command_key_lexmin_lexmax": rf"\s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX} \s*",
    "command_key_start_end_withscores_x": rf"""
        \s+ {KEY} \s+ {START} \s+ {END} (\s+ {WITHSCORES})? \s*""",
    "command_key_lexmin_lexmax_limit_offset_count": rf"""
        \s+ {KEY} \s+ {LEXMIN} \s+ {LEXMAX}
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_key_min_max_withscore_x_limit_offset_count_x": rf"""
        \s+ {KEY} \s+ {MIN} \s+ {MAX} (\s+ {WITHSCORES})?
        (\s+ {LIMIT} \s+ {OFFSET} \s+ {COUNT})? \s*""",
    "command_cursor_match_pattern_count_type": rf"""
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})?
        (\s+ {COUNT_CONST} \s+ {COUNT})? (\s+ {TYPE_CONST} \s+ {TYPE})? \s*""",
    "command_key_cursor_match_pattern_count": rf"""\s+ {KEY}
        \s+ {CURSOR} (\s+ {MATCH} \s+ {PATTERN})? (\s+ {COUNT_CONST} \s+ {COUNT})? \s*""",
    "command_key_fields": rf"\s+ {KEY} \s+ {FIELDS} \s*",
    "command_key_field": rf"\s+ {KEY} \s+ {FIELD} \s*",
    "command_key_field_delta": rf"\s+ {KEY} \s+ {FIELD} \s+ {DELTA} \s*",
    "command_key_field_float": rf"\s+ {KEY} \s+ {FIELD} \s+ {FLOAT} \s*",
    "command_key_fieldvalues": rf"\s+ {KEY} (\s+ {FIELD} \s+ {VALUE})+ \s*",
    "command_slowlog": rf"\s+ {SLOWLOGSUB} \s+ {NUM} \s*",
    "command_switch": rf"\s+ {SWITCH} \s*",
    "command_schedulex": rf"(\s+ {SCHEDULE})? \s*",
    "command_clientkill": rf"""
        (
            (\s+ {IP_PORT})|
            (\s+ {ADDR} \s+ {IP_PORT})|
            (\s+ {LADDR} \s+ {IP_PORT})|
            (\s+ {CONST_ID} \s+ {CLIENTID})|
            (\s+ {TYPE_CONST} \s+ {CONNTYPE})|
            (\s+ {CONST_USER} \s+ {USERNAME})|
            (\s+ {SKIPME} \s+ {YES})
        )+ \s*""",
    "command_migrate": rf"""
        \s+ {HOST} \s+ {PORT}
        \s+ {KEY} \s+ {INDEX} \s+ {TIMEOUT}
        (\s+ {MIGRATECHOICE})?
        (
            (\s+ {AUTH} \s+ {PASSWORD})|
            (\s+ {AUTH} \s+ {USERNAME} \s+ {PASSWORD})
        )?
        (\s+ {CONST_KEYS} \s+ {KEYS})?
    \s*""",
    "command_restore": rf"""\s+ {KEY}
        \s+ {TIMEOUT} \s+ {VALUE} (\s+ {SUBRESTORE} \s+ {SECOND})? \s*""",
    "command_pubsubcmd_channels": rf"\s+ {PUBSUBCMD} (\s+ {CHANNEL})+ \s*",
    "command_channel_message": rf"\s+ {CHANNEL} \s+ {MESSAGE} \s*",
    "command_channels": rf"(\s+ {CHANNEL})+ \s*",
    "command_lua_any": rf"""(\s+"{DOUBLE_LUA}")? (\s+'{SINGLE_LUA}')? \s+ {ANY} \s*""",
    "command_scriptdebug": rf"\s+ {SCRIPTDEBUG} \s*",
    "command_shutdown": rf"\s+ {SHUTDOWN} \s*",
    "command_key_start_end_countx": rf"""\s+ {KEY}
        \s+ {STREAM_ID}
        \s+ {STREAM_ID}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        \s*""",
    "command_xgroup": rf"""
        (
            (\s+ {STREAM_CREATE} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_SETID} \s+ {KEY} \s+ {GROUP} \s+ {STREAM_ID})|
            (\s+ {STREAM_DESTROY} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_DELCONSUMER} \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER})|
            (\s+ {HELP})
        )
        \s*""",
    "command_key_group_ids": rf"""
        \s+ {KEY} \s+ {GROUP} (\s+ {STREAM_ID})+ \s*""",
    "command_key_ids": rf"""
        \s+ {KEY} (\s+ {STREAM_ID})+ \s*""",
    "command_xinfo": rf"""
        (
            (\s+ {STREAM_CONSUMERS} \s+ {KEY} \s+ {GROUP})|
            (\s+ {STREAM_GROUPS} \s+ {KEY})|
            (\s+ {STREAM} \s+ {KEY}
                (\s+ {FULL_CONST})?
                (\s+ {COUNT_CONST} \s+ {COUNT})?
            )|
            (\s+ {HELP})
        )
        \s*""",
    "command_xpending": rf"""
        \s+ {KEY} \s+ {GROUP}
        (\s+ {STREAM_ID} \s+ {STREAM_ID} \s+ {COUNT})?
        (\s+ {CONSUMER})?
        \s*""",
    "command_xadd": rf"""
        \s+ {KEY}
        (\s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT})?
        \s+ {STREAM_ID}
        (\s+ {SFIELD} \s+ {SVALUE})+ \s*""",
    "command_key_maxlen": rf"""
        \s+ {KEY} \s+ {MAXLEN} (\s+ {APPROXIMATELY})? \s+ {COUNT}
        \s*""",
    "command_xclaim": rf"""
        \s+ {KEY} \s+ {GROUP} \s+ {CONSUMER} \s+ {MILLISECOND}
        (\s+ {STREAM_ID})+
        (\s+ {IDLE} \s+ {MILLISECOND})?
        (\s+ {TIME} \s+ {TIMESTAMP})?
        (\s+ {RETRYCOUNT} \s+ {COUNT})?
        (\s+ {FORCE})?
        (\s+ {JUSTID})?
        \s*""",
    "command_xread": rf"""
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_xreadgroup": rf"""
        \s+ {STREAM_GROUP} \s+ {GROUP} \s+ {CONSUMER}
        (\s+ {COUNT_CONST} \s+ {COUNT})?
        (\s+ {BLOCK} \s+ {MILLISECOND})?
        (\s+ {NOACK})?
        \s+ {STREAMS}
        \s+ {KEYS}
        (\s+ {STREAM_ID})+
        \s*""",
    "command_bitfield": rf"""
        \s+ {KEY}
        (
            (\s+ {GET} \s+ {INTTYPE} \s+ {SHARP_OFFSET})|
            (\s+ {SET} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {INCRBY} \s+ {INTTYPE} \s+ {SHARP_OFFSET} \s+ {VALUE})|
            (\s+ {OVERFLOW} \s+ {OVERFLOW_OPTION})
        )+
        \s*""",
    "command_replicationid_offset": rf"\s+ {REPLICATIONID} \s+ {OFFSET} \s*",
    "command_graphevent": rf"\s+ {GRAPHEVENT} \s*",
    "command_graphevents": rf"(\s+ {GRAPHEVENT})* \s*",
    # before redis 5: lolwut 5 1
    # start from redis 6: lolwut VERSION 5 1
    "command_version": rf"(\s+ {VERSION} \s+ {VERSION_NUM})? (\s+ {ANY})? \s*",
    "command_client_tracking": rf"""
        \s+ {ON_OFF}
        (
            (\s+ {REDIRECT_CONST} \s+ {CLIENTID})|
            (\s+ {PREFIX_CONST} \s+ {PREFIXES})|
            (\s+ {BCAST_CONST})|
            (\s+ {OPTIN_CONST})|
            (\s+ {OPTOUT_CONST})|
            (\s+ {NOLOOP_CONST})
        )*
        \s*""",
    "command_categorynamex": rf"(\s+ {CATEGORYNAME})? \s*",
    "command_usernames": rf"(\s+ {USERNAME})+ \s*",
    "command_username": rf"\s+ {USERNAME} \s*",
    "command_count_or_resetx": rf"( (\s+ {COUNT}) | (\s+ {RESET_CONST}) )? \s*",
    "command_username_rules": rf"\s+ {USERNAME} (\s+ {RULE})* \s*",
    "command_count": rf"(\s+ {COUNT})? \s*",
    "command_stralgo": rf"""
        (
            \s+ {STR_ALGO}
            (
                (\s+ {CONST_KEYS} \s+ {KEYS})|
                (\s+ {STRINGS_CONST} \s+ {VALUES})
            )
            (\s+ {IDX_CONST})?
            (\s+ {LEN_CONST})?
            (\s+ {MINMATCHLEN_CONST} \s+ {LEN})?
            (\s+ {WITHMATCHLEN_CONST})?
        )
    \s*""",
    "command_lpos": rf"""
        \s+ {KEY} \s+ {ELEMENT}
        (
            (\s+ {RANK_CONST} \s+ {RANK})|
            (\s+ {COUNT_CONST} \s+ {COUNT})|
            (\s+ {MAXLEN} \s+ {LEN})
        )*
        \s*""",
    "command_key_key_lr_lr_timeout": rf"""
        \s+ {KEY} \s+ {KEY}
        \s+ {LR_CONST} \s+ {LR_CONST}
        \s+ {TIMEOUT} \s*""",
    "command_copy": rf"""
        \s+ {KEY} \s+ {KEY}
        (\s+ {DB_CONST} \s+ {INDEX})?
        (\s+ {REPLACE_CONST})?
        \s*""",
    "command_failover": rf"""
        (\s+ {TO_CONST} \s+ {HOST} \s+ {PORT} (\s+ {FORCE})? )?
        (\s+ {ABORT_CONST})?
        (\s+ {TIMEOUT_CONST} \s+ {MILLISECOND})?
        \s*""",
    "command_key_expire": rf"""
        \s+ {KEY}
        (
            (\s+ {EXPIRATION} \s+ {MILLISECOND})|
            (\s+ {PXAT_CONST} \s+ {TIMESTAMPMS})|
            (\s+ {EXAT_CONST} \s+ {TIMESTAMP})
        )?
        \s*""",
    "command_key_count_withvalues": rf"""
        \s+ {KEY}
        (\s+ {COUNT} (\s+ {WITHVALUES_CONST})?)?
        \s*""",
}

pipeline = r"(?P<shellcommand>\|.*)?"


@lru_cache(maxsize=256)
def get_command_grammar(command):
    """
    :param command: command name in upper case. This command must be raw user
        input, otherwise can't match in lexer, cause this command to be invalid;
    """
    syntax_name = command2syntax[" ".join(command.split()).upper()]
    syntax = GRAMMAR.get(syntax_name)

    # If a command is not supported yet, (e.g. command from latest version added
    # by Redis recently, or command from third Redis module.) return a default
    # grammar, so the lexer and completion won't be activated.
    if syntax is None:
        return command_grammar
    # prepend command token for this syntax
    command_allow_multi_spaces = command.replace(r" ", r"\s+")
    syntax = rf"\s* (?P<command>{command_allow_multi_spaces}) " + syntax
    # allow user input pipeline to redirect to shell, like `get json | jq .`
    syntax += pipeline

    logger.info(f"syxtax: {syntax}")

    return compile(syntax)
