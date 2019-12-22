"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response, completers: GrammarCompleter) -> formatted result(str)
"""
import time
import logging
from prompt_toolkit.formatted_text import FormattedText
from distutils.version import StrictVersion

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
    if isinstance(origin, int):
        return str(origin)
    elif isinstance(origin, list):
        return [_ensure_str(b) for b in origin]
    elif isinstance(origin, bytes):
        if decode:
            return origin.decode(decode)
        return _literal_bytes(origin)
    else:
        raise Exception(f"Unkown type: {type(origin)}, origin: {origin}")


def render_bulk_string(value, completers=None):
    if config.raw:
        if value is None:
            return b""
        return value
    if value is None:
        return NIL
    return _double_quotes(_ensure_str(value))


def render_bulk_string_decode(value, completers=None):
    """Only for server group commands, no double quoted,  displayed.
    Display use UTF-8.
    """
    decoded = value.decode()
    splitted = "\n".join(decoded.splitlines())
    return splitted


def _render_pair(pairs, indent):
    keys = [item for item in pairs[::2]]
    values = [item for item in pairs[1::2]]
    rendered = []
    for key, value in zip(keys, values):
        key = _ensure_str(key, decode="utf-8")
        value = _ensure_str(value, decode="utf-8")
        rendered.append(("class:string", f"{' '*4*indent}{key}: "))
        if isinstance(value, list):
            rendered.append(NEWLINE_TUPLE)
            rendered.extend(_render_pair(value, indent + 1))
        else:
            rendered.append(("class:value", value))
        rendered.append(NEWLINE_TUPLE)
    return rendered[:-1]  # remove last newline


def render_nested_pair(value, completers=None):
    """
    For redis internel responses.
    Always decode with utf-8
    Render nested list.
    Items come as pairs.
    """
    if config.raw:
        return render_list(value)
    return FormattedText(_render_pair(value, 0))


def render_int(value, completers=None):
    if config.raw:
        if value is None:
            return b""
        return str(value).encode()
    if value is None:
        return NIL
    return FormattedText([("class:type", "(integer) "), ("", str(value))])


def render_unixtime(value, completers=None):
    rendered_int = render_int(value, completers)
    if config.raw:
        return rendered_int
    explained_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(value)))
    rendered_int.extend(
        [NEWLINE_TUPLE, ("class:type", "(local time)"), ("", " "), ("", explained_date)]
    )
    return rendered_int


def render_time(value, completers=None):
    if config.raw:
        return render_list(value)
    unix_timestamp, millisecond = value[0].decode(), value[1].decode()
    explained_date = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(int(unix_timestamp))
    )
    rendered = [
        ("class:type", "(unix timestamp) "),
        ("", unix_timestamp),
        NEWLINE_TUPLE,
        ("class:type", "(millisecond) "),
        ("", millisecond),
        NEWLINE_TUPLE,
        ("class:type", "(convert to local timezone) "),
        ("", f"{explained_date}.{millisecond}"),
    ]
    return FormattedText(rendered)


def _render_raw_list(bytes_items):
    flatten_items = []
    for item in bytes_items:
        if item is None:
            flatten_items.append(b"")
        elif isinstance(item, bytes):
            flatten_items.append(item)
        elif isinstance(item, int):
            flatten_items.append(str(item).encode())
        elif isinstance(item, list):
            flatten_items.append(_render_raw_list(item))
    return b"\n".join(flatten_items)


def _render_list(byte_items, str_items, style=None, pre_space=0):
    """Complute the newline/number-width/lineno,
    render list to FormattedText
    """
    if config.raw:
        return _render_raw_list(byte_items)

    if not str_items:
        return EMPTY_LIST

    index_width = len(str(len(str_items)))
    rendered = []
    for index, item in enumerate(str_items):
        indent_spaces = (index + 1 != 1) * pre_space * " "
        if indent_spaces:
            rendered.append(("", indent_spaces))  # add a space before item

        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        # list item
        rendered.append(("", " "))  # add a space before item
        if item is None:
            rendered.append(NIL_TUPLE)
        elif isinstance(item, str):
            rendered.append((style, item))
        else:  # it's a nested list
            # if config.raw == True, never will get there
            sublist = _render_list(None, item, style, pre_space + index_width + 2)
            rendered.extend(sublist)

        # add a newline for eachline
        if index + 1 < len(str_items):
            rendered.append(NEWLINE_TUPLE)
    return rendered


def render_list(text, completer=None):
    """
    Render callback for redis Array Reply, can't render nested list
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
    rendered = _render_list(text, str_items, "class:string")
    if config.raw:
        return rendered
    return FormattedText(rendered)


def render_list_or_string(text, completer=None):
    if isinstance(text, list):
        return render_list(text, completer)
    return render_bulk_string(text, completer)


def render_string_or_int(text, completer=None):
    if isinstance(text, int):
        return render_int(text, completer)
    return render_bulk_string(text, completer)


def render_error(error_msg):
    # FIXME raw
    text = _ensure_str(error_msg)
    return FormattedText([("class:type", "(error) "), ("class:error", text)])


def render_simple_string(text, completer):
    """
    If response is b'OK', render ok with success color.
    else render message with Error color.
    """
    # FIXME raw
    if text is None:
        return NIL
    text = _ensure_str(text)
    return FormattedText([("class:success", text)])


def render_transaction_queue(text, completer):
    """
    Used when client session is in a transaction.

    Response message should be "QUEUE" or Error.
    """
    # FIXME raw
    text = _ensure_str(text)
    assert text == "QUEUED"
    return FormattedText([("class:queued", text)])


def _update_completer_then_render(
    items, completer, complter_name, style, completer_iter_step=1
):
    """
    :param completer_iter_step: every `completer_iter_step` items is used to update complters
    """
    str_items = _ensure_str(items)
    # update completers
    if completer:
        token_completer = completer.completers[complter_name]
        token_completer.touch_words(str_items[::completer_iter_step])
        logger.debug(f"[Completer] {complter_name} completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")
    double_quoted = _double_quotes(str_items)
    rendered = _render_list(items, double_quoted, style)
    if config.raw:
        return rendered
    return FormattedText(rendered)


def _update_completer_then_render_withscores(items, completer):
    if not items:
        return EMPTY_LIST
    complter_name = "member"
    str_items = _ensure_str(items)

    members = [item for item in str_items[::2]]
    scores = [item for item in str_items[1::2]]
    logger.debug(f"[MEMBERS] {members}")
    logger.debug(f"[SCORES] {scores}")
    # update completers
    if completer:
        token_completer = completer.completers[complter_name]
        token_completer.touch_words(members)
        logger.debug(f"[Completer] {complter_name} completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")
    # render display
    double_quoted = _double_quotes(members)
    index_width = len(str(len(double_quoted)))
    score_width = max(len(score) for score in scores)
    rendered = []
    for index, item in enumerate(double_quoted):
        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        # add a space between index and member
        rendered.append(("", " "))
        # add score
        rendered.append(("class:integer", f"{scores[index]:{score_width}} "))
        # add member
        if item is None:
            rendered.append(NIL_TUPLE)
        else:
            rendered.append(("class:member", item))

        # add a newline for eachline
        if index + 1 < len(double_quoted):
            rendered.append(NEWLINE_TUPLE)
    return FormattedText(rendered)


def command_keys(items, completer):
    return _update_completer_then_render(items, completer, "key", "class:key")


def render_members(items, completer):
    if config.withscores:
        if config.raw:
            return _update_completer_then_render(
                items, completer, "member", "class:member", completer_iter_step=2
            )
        return _update_completer_then_render_withscores(items, completer)
    return _update_completer_then_render(
        items, completer, "member", "class:member", completer_iter_step=1
    )


def _render_scan(render_response, response, completer):
    cursor, responses = response
    if config.raw:
        return b"\n".join([cursor, render_response(responses, completer)])

    rendered = [
        ("class:type", "(cursor) "),
        ("class:integer", cursor.decode()),
        ("", "\n"),
    ]
    rendered_keys = render_response(responses, completer)
    return FormattedText(rendered + rendered_keys)


def command_scan(response, completer):
    """
    Render Scan command result.
    see: https://redis.io/commands/scan
    """
    return _render_scan(command_keys, response, completer)


def command_sscan(response, completer):
    return _render_scan(render_members, response, completer)


def command_zscan(response, completer):
    return _render_scan(render_members, response, completer)


def command_hscan(response, completer):
    return _render_scan(render_hash_pairs, response, completer)


def command_hkeys(response, completer):
    return _update_completer_then_render(response, completer, "field", "class:field")


def render_hash_pairs(response, completer):
    if config.raw:
        return _update_completer_then_render(
            response, completer, "field", "class:field", completer_iter_step=2
        )
    # render hash pairs
    if not response:
        return EMPTY_LIST
    complter_name = "field"
    str_items = _ensure_str(response)
    fields = str_items[0::2]
    values = str_items[1::2]
    # update completers
    if completer:
        field_completer = completer.completers[complter_name]
        field_completer.touch_words(fields)
        logger.debug(f"[Completer] {complter_name} completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")
    # render display
    index_width = len(str(len(fields)))
    values_quoted = _double_quotes(values)
    fields_quoted = _double_quotes(fields)
    rendered = []
    for index, item in enumerate(fields_quoted):
        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        rendered.append(("", " "))
        rendered.append(("class:field", item))
        rendered.append(NEWLINE_TUPLE)
        rendered.append(("", " " * (len(index_const_width) + 1)))
        value = values_quoted[index]
        if value is None:
            rendered.append(NIL_TUPLE)
        else:
            rendered.append(("class:string", value))

        # add a newline for eachline
        if index + 1 < len(fields):
            rendered.append(NEWLINE_TUPLE)
    return FormattedText(rendered)


def render_slowlog(raw, completers=None):
    if config.raw:
        return _render_raw_list(raw)
    fields = ["Slow log id", "Start at", "Running time(ms)", "Command"]
    if StrictVersion(config.version) > StrictVersion("4.0"):
        fields.extend(["Client IP and port", "Client name"])

    rendered = []
    text = _ensure_str(raw)
    index_width = len(str(len(text)))
    for index, slowlog in enumerate(text):
        index_str = f"{index+1:{index_width}}) "
        rendered.append(("", index_str))
        for field, value in zip(fields, slowlog):
            if field == "Command":
                value = " ".join(value)
            if field != "Slow log id":
                display_field = " " * len(index_str) + field
            else:
                display_field = field
            logger.debug(f"field: {field}, value: {value}")
            rendered.extend(
                [
                    ("class:field", f"{display_field}: "),
                    ("class:string", value),
                    NEWLINE_TUPLE,
                ]
            )

    return FormattedText(rendered[:-1])


# TODO
# special list render, bzpopmax, key-value pair
