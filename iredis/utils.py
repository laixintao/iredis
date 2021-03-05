import re
import sys
import time
import logging
from collections import namedtuple
from urllib.parse import parse_qs, unquote, urlparse

from prompt_toolkit.formatted_text import FormattedText

from iredis.exceptions import InvalidArguments


logger = logging.getLogger(__name__)

_last_timer = time.time()
_timer_counter = 0
sperator = re.compile(r"\s")
logger.debug(f"[timer] start on {_last_timer}")


def timer(title):
    global _last_timer
    global _timer_counter

    now = time.time()
    tick = now - _last_timer
    logger.debug(f"[timer{_timer_counter:2}] {tick:.8f} -> {title}")

    _last_timer = now
    _timer_counter += 1


def nativestr(x):
    return x if isinstance(x, str) else x.decode("utf-8", "replace")


def literal_bytes(b):
    if isinstance(b, bytes):
        return str(b)[2:-1]
    return b


def _valid_token(words):
    token = "".join(words).strip()
    if token:
        yield token


def strip_quote_args(s):
    """
    Given string s, split it into args.(Like bash paring)
    Handle with all quote cases.

    Raise ``InvalidArguments`` if quotes not match

    :return: args list.
    """
    word = []
    in_quote = None
    pre_back_slash = False
    for char in s:
        if in_quote:
            # close quote
            if char == in_quote:
                if not pre_back_slash:
                    yield "".join(word)
                    word = []
                    in_quote = None
                else:
                    # previous char is \ , merge with current "
                    word[-1] = char
            else:
                word.append(char)
        # not in quote
        else:
            # sperator
            if sperator.match(char):
                if word:
                    yield "".join(word)
                    word = []
            # open quotes
            elif char in ["'", '"']:
                in_quote = char
            else:
                word.append(char)
        if char == "\\" and not pre_back_slash:
            pre_back_slash = True
        else:
            pre_back_slash = False

    if word:
        yield "".join(word)
    # quote not close
    if in_quote:
        raise InvalidArguments("Invalid argument(s)")


type_convert = {"posix time": "time"}


def parse_argument_to_formatted_text(
    name, _type, is_option, style_class="bottom-toolbar"
):
    result = []
    if isinstance(name, str):
        _type = type_convert.get(_type, _type)
        if is_option:
            result.append((f"class:{style_class}.{_type}", f" [{name}]"))
        else:
            result.append((f"class:{style_class}.{_type}", f" {name}"))
    elif isinstance(name, list):
        for inner_name, inner_type in zip(name, _type):
            inner_type = type_convert.get(inner_type, inner_type)
            if is_option:
                result.append((f"class:{style_class}.{inner_type}", f" [{inner_name}]"))
            else:
                result.append((f"class:{style_class}.{inner_type}", f" {inner_name}"))
    else:
        raise Exception()
    return result


def compose_command_syntax(command_info, style_class="bottom-toolbar"):
    command_style = f"class:{style_class}.command"
    const_style = f"class:{style_class}.const"
    args = []
    if command_info.get("arguments"):
        for argument in command_info["arguments"]:
            if argument.get("command"):
                # command [
                args.append((command_style, " [" + argument["command"]))
                if argument.get("enum"):
                    enums = "|".join(argument["enum"])
                    args.append((const_style, f" [{enums}]"))
                elif argument.get("name"):
                    args.extend(
                        parse_argument_to_formatted_text(
                            argument["name"],
                            argument["type"],
                            argument.get("optional"),
                            style_class=style_class,
                        )
                    )
                # ]
                args.append((command_style, "]"))
            elif argument.get("enum"):
                enums = "|".join(argument["enum"])
                args.append((const_style, f" [{enums}]"))

            else:
                args.extend(
                    parse_argument_to_formatted_text(
                        argument["name"],
                        argument["type"],
                        argument.get("optional"),
                        style_class=style_class,
                    )
                )
    return args


def command_syntax(command, command_info):
    """
    Get command syntax based on redis-doc/commands.json

    :param command: Command name in uppercase
    :param command_info: dict loaded from commands.json, only for
        this command.
    """
    comamnd_group = command_info["group"]
    bottoms = [
        ("class:bottom-toolbar.group", f"({comamnd_group}) "),
        ("class:bottom-toolbar.command", f"{command}"),
    ]  # final display FormattedText

    bottoms += compose_command_syntax(command_info)

    if "since" in command_info:
        since = command_info["since"]
        bottoms.append(("class:bottom-toolbar.since", f"   since: {since}"))
    if "complexity" in command_info:
        complexity = command_info["complexity"]
        bottoms.append(("class:bottom-toolbar.complexity", f" complexity:{complexity}"))

    return FormattedText(bottoms)


def _literal_bytes(b):
    """
    convert bytes to printable text.

    backslash and double-quotes will be escaped by
    backslash.
    "hello\" -> \"hello\\\"

    we don't add outer double quotes here, since
    completer also need this function's return value
    to patch completers.

    b'hello' -> "hello"
    b'double"quotes"' -> "double\"quotes\""
    """
    s = str(b)
    s = s[2:-1]  # remove b' '
    # unescape single quote
    s = s.replace(r"\'", "'")
    return s


def ensure_str(origin, decode=None):
    """
    Ensure is string, for display and completion.

    Then add double quotes

    Note: this method do not handle nil, make sure check (nil)
          out of this method.
    """
    if origin is None:
        return None
    if isinstance(origin, str):
        return origin
    if isinstance(origin, int):
        return str(origin)
    elif isinstance(origin, list):
        return [ensure_str(b) for b in origin]
    elif isinstance(origin, bytes):
        if decode:
            return origin.decode(decode)
        return _literal_bytes(origin)
    else:
        raise Exception(f"Unkown type: {type(origin)}, origin: {origin}")


def double_quotes(unquoted):
    """
    Display String like redis-cli.
    escape inner double quotes.
    add outer double quotes.

    :param unquoted: list, or str
    """
    if isinstance(unquoted, str):
        # escape double quote
        escaped = unquoted.replace('"', '\\"')
        return f'"{escaped}"'  # add outer double quotes
    elif isinstance(unquoted, list):
        return [double_quotes(item) for item in unquoted]


def exit():
    """
    Exit IRedis REPL
    """
    print("Goodbye!")
    sys.exit()


def convert_formatted_text_to_bytes(formatted_text):
    to_render = [text for style, text in formatted_text]
    return "".join(to_render).encode()


DSN = namedtuple("DSN", "scheme host port path db username password")


def parse_url(url, db=0):
    """
    Return a Redis client object configured from the given URL

    For example::

        redis://[[username]:[password]]@localhost:6379/0
        rediss://[[username]:[password]]@localhost:6379/0
        unix://[[username]:[password]]@/path/to/socket.sock?db=0

    Three URL schemes are supported:

    - ```redis://``
      <http://www.iana.org/assignments/uri-schemes/prov/redis>`_ creates a
      normal TCP socket connection
    - ```rediss://``
      <http://www.iana.org/assignments/uri-schemes/prov/rediss>`_ creates a
      SSL wrapped TCP socket connection
    - ``unix://`` creates a Unix Domain Socket connection

    There are several ways to specify a database number. The parse function
    will return the first specified option:
        1. A ``db`` querystring option, e.g. redis://localhost?db=0
        2. If using the redis:// scheme, the path argument of the url, e.g.
           redis://localhost/0
        3. The ``db`` argument to this function.

    If none of these options are specified, db=0 is used.
    """
    url = urlparse(url)

    scheme = url.scheme
    path = unquote(url.path) if url.path else None
    # We only support redis://, rediss:// and unix:// schemes.
    # if scheme is ``unix``, read ``db`` from query string
    # otherwise read ``db`` from path
    if url.scheme == "unix":
        qs = parse_qs(url.query)
        if "db" in qs:
            db = int(qs["db"][0] or db)
    elif url.scheme in ("redis", "rediss"):
        scheme = url.scheme
        if path:
            try:
                db = int(path.replace("/", ""))
                path = None
            except (AttributeError, ValueError):
                pass
    else:
        valid_schemes = ", ".join(("redis://", "rediss://", "unix://"))
        raise ValueError(
            "Redis URL must specify one of the following" "schemes (%s)" % valid_schemes
        )

    username = unquote(url.username) if url.username else None
    password = unquote(url.password) if url.password else None
    hostname = unquote(url.hostname) if url.hostname else None
    port = url.port

    return DSN(scheme, hostname, port, path, db, username, password)
