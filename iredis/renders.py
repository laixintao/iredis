"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response, completers: GrammarCompleter) -> formatted result(str)
"""
import logging
from prompt_toolkit.formatted_text import FormattedText

from .config import config

logger = logging.getLogger(__name__)
NEWLINE_TUPLE = ("", "\n")
NIL_TUPLE = ("class:type", "(nil)")
NIL = FormattedText([NIL_TUPLE])
EMPTY_LIST = FormattedText([("class:type", "(empty list or set)")])


def _literal_bytes(b):
    """
    convert bytes to printable text.

    backslash and double-quotes will be escaped by
    backslash.
    "hello\" -> \"hello\\\"

    we don't add outter double quotes here, since
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


def _double_quotes(unquoted):
    """
    Display String like redis-cli.
    escape inner double quotes.
    add outter double quotes.

    :param unquoted: list, or str
    """
    if isinstance(unquoted, str):
        # escape double quote
        escaped = unquoted.replace('"', '\\"')
        return f'"{escaped}"'  # add outter double quotes
    elif isinstance(unquoted, list):
        return [_double_quotes(item) for item in unquoted]


def _ensure_str(origin, decode=None):
    """
    Ensure is string, for display and completion.

    Then add double quotes

    Note: this method do not handle nil, make sure check (nil)
          out of this method.
    """
    if isinstance(origin, str):
        return origin
    elif isinstance(origin, list):
        return [_ensure_str(b) for b in origin]
    elif isinstance(origin, bytes):
        return _literal_bytes(origin)
    else:
        raise Exception(f"Unkown type: {type(origin)}, origin: {origin}")


def render_simple_strings(value, completers=None):
    if config.raw:
        return value
    if value is None:
        return NIL
    return _double_quotes(_ensure_str(value))


def render_int(value, completers=None):
    if config.raw:
        return str(value).encode()
    return FormattedText([("class:type", "(integer) "), ("", str(value))])


def _render_list(byte_items, str_items, style=None):
    """Complute the newline/number-width/lineno,
    render list to FormattedText
    """
    if config.raw:
        return b"\n".join(text if text else b"" for text in byte_items)
    index_width = len(str(len(str_items)))
    rendered = []
    if not str_items:
        return EMPTY_LIST
    for index, item in enumerate(str_items):
        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        # list item
        rendered.append(("", " "))  # add a space before item
        if item is None:
            rendered.append(NIL_TUPLE)
        else:
            rendered.append((style, item))

        # add a newline for eachline
        if index + 1 < len(str_items):
            rendered.append(NEWLINE_TUPLE)
    return FormattedText(rendered)


def render_list(text, completer):
    """
    Render callback for redis Array Reply
    Note: Cloud be null in it.
    """
    str_items = []
    for item in text:
        if item is None:
            str_items.append(None)
        else:
            str_item = _ensure_str(item)
            double_quoted = _double_quotes(str_item)
            str_items.append(double_quoted)
    return _render_list(text, str_items, "class:string")


def render_list_or_string(text, completer=None):
    if isinstance(text, list):
        return render_list(text, completer)
    return render_simple_strings(text, completer)


def render_error(error_msg):
    text = _ensure_str(error_msg)
    return FormattedText([("class:type", "(error) "), ("class:error", text)])


def render_ok(text, completer):
    """
    If response is b'OK', render ok with success color.
    else render message with Error color.
    """
    if text is None:
        return NIL
    text = _ensure_str(text)
    assert text == "OK"
    return FormattedText([("class:success", text)])


def render_transaction_queue(text, completer):
    """
    Used when client session is in a transaction.

    Response message should be "QUEUE" or Error.
    """
    text = _ensure_str(text)
    assert text == "QUEUED"
    return FormattedText([("class:queued", text)])


def command_keys(items, completer):
    str_items = _ensure_str(items)

    # update completers
    if completer:
        key_completer = completer.completers["key"]
        key_completer.touch_words(str_items)
        logger.debug(f"[Completer] key completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")

    # render is render, completer is completer
    # render and completer are in same function but code are splitted.
    # Give back to Ceasar what is Ceasar's and to God what is God's.
    double_quoted = _double_quotes(str_items)
    rendered = _render_list(items, double_quoted, "class:key")
    return rendered
