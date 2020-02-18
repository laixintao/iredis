"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response) -> formatted result(str)
"""
import logging
import time
from distutils.version import StrictVersion

from prompt_toolkit.formatted_text import FormattedText

from .commands_csv_loader import command2callback
from .config import config
from .utils import double_quotes, ensure_str, nativestr

logger = logging.getLogger(__name__)
NEWLINE_TUPLE = ("", "\n")
NIL_TUPLE = ("class:type", "(nil)")
NIL = FormattedText([NIL_TUPLE])
EMPTY_LIST = FormattedText([("class:type", "(empty list or set)")])


class OutputRender:
    """Render redis output
    """

    @staticmethod
    def dynamic_render(command_name, response):
        """Dynamic render output due to command name."""
        command_upper = command_name.upper()
        callback_name = command2callback.get(command_upper)
        # else, use defined callback
        if callback_name is None:
            logger.warning("unknown command %s", command_name)
            return response

        if not hasattr(OutputRender, callback_name):
            # FIXME
            # not implemented command, use no conversion
            # this condition should be deleted finally
            logger.warning(
                "command `%s`'s callback %s is not implemented",
                command_name,
                callback_name,
            )
            return response

        callback = getattr(OutputRender, callback_name)
        rendered = callback(response)
        logger.info(f"[rendered] {rendered}")
        return rendered

    @staticmethod
    def render_bulk_string(value):
        if config.raw:
            if value is None:
                return b""
            return value
        if value is None:
            return NIL
        return double_quotes(ensure_str(value))

    @staticmethod
    def render_bulk_string_decode(value):
        """
        Only for server group commands, no double quoted, always displayed as
        utf-8 decoded.
        """
        decoded = nativestr(value)
        splitted = "\n".join(decoded.splitlines())  # get rid of last newline
        return splitted

    @staticmethod
    def render_nested_pair(value):
        """
        For redis internel responses.
        Always decode with utf-8
        Render nested list.
        Items come as pairs.
        """
        if config.raw:
            return OutputRender.render_list(value)
        return FormattedText(_render_pair(value, 0))

    @staticmethod
    def render_int(value):
        if config.raw:
            if value is None:
                return b""
            return str(value).encode()
        if value is None:
            return NIL
        return FormattedText([("class:type", "(integer) "), ("", str(value))])

    @staticmethod
    def render_unixtime(value):
        rendered_int = OutputRender.render_int(value)
        if config.raw:
            return rendered_int
        explained_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(value)))
        rendered_int.extend(
            [
                NEWLINE_TUPLE,
                ("class:type", "(local time)"),
                ("", " "),
                ("", explained_date),
            ]
        )
        return rendered_int

    @staticmethod
    def render_time(value):
        if config.raw:
            return OutputRender.render_list(value)
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

    @staticmethod
    def render_list(text):
        """
        Render callback for redis Array Reply
        Note: Cloud be null in it.
        """
        str_items = []
        for item in text:
            if item is None:
                str_items.append(None)
            else:
                str_item = ensure_str(item)
                double_quoted = double_quotes(str_item)
                str_items.append(double_quoted)
        rendered = _render_list(text, str_items, "class:string")
        if config.raw:
            return rendered
        return FormattedText(rendered)

    @staticmethod
    def render_list_or_string(text):
        if isinstance(text, list):
            return OutputRender.render_list(text)
        return OutputRender.render_bulk_string(text)

    @staticmethod
    def render_string_or_int(text):
        if isinstance(text, int):
            return OutputRender.render_int(text)
        return OutputRender.render_bulk_string(text)

    @staticmethod
    def render_error(error_msg):
        if config.raw:
            return error_msg
        text = ensure_str(error_msg)
        return FormattedText([("class:type", "(error) "), ("class:error", text)])

    @staticmethod
    def render_simple_string(text):
        """
        If response is b'OK', render ok with success color.
        else render message with Error color.
        """
        if config.raw:
            return text
        if text is None:
            return NIL
        text = ensure_str(text)
        return FormattedText([("class:success", text)])

    @staticmethod
    def render_transaction_queue(text):
        """
        Used when client session is in a transaction.

        Response message should be "QUEUE" or Error.
        """
        # FIXME raw
        text = ensure_str(text)
        return FormattedText([("class:queued", text)])

    @staticmethod
    def render_members(items):
        if config.withscores:
            if config.raw:
                return _update_completer_then_render(items, "class:member")
            return _update_completer_then_render_withscores(items)
        return _update_completer_then_render(items, "class:member")

    @staticmethod
    def render_hash_pairs(response):
        if config.raw:
            return _update_completer_then_render(response, "class:field")
        # render hash pairs
        if not response:
            return EMPTY_LIST
        str_items = ensure_str(response)
        fields = str_items[0::2]
        values = str_items[1::2]
        # render display
        index_width = len(str(len(fields)))
        values_quoted = double_quotes(values)
        fields_quoted = double_quotes(fields)
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

    @staticmethod
    def render_slowlog(raw):
        if config.raw:
            return _render_raw_list(raw)
        fields = ["Slow log id", "Start at", "Running time(ms)", "Command"]
        if StrictVersion(config.version) > StrictVersion("4.0"):
            fields.extend(["Client IP and port", "Client name"])

        rendered = []
        text = ensure_str(raw)
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

    @staticmethod
    def render_subscribe(raw):
        """
        message type;
        channel;
        message;
        see: https://redis.io/topics/pubsub#format-of-pushed-messages
        """
        logger.info(raw)
        if config.raw:
            return OutputRender.render_list(raw)
        if raw[1] is None:
            raw[1] = "all"
        mtype, *channel, message = ensure_str(raw)
        # PUNSUBSCRIBE, 4 args
        channel = ":".join(channel)
        return FormattedText(
            [
                ("", f"{mtype:<9} from "),  # 9 is len("subscribe")
                ("class:channel", channel),
                ("", ": "),  # 9 is len("subscribe")
                ("class:string", f"{message}"),
            ]
        )

    @staticmethod
    def command_keys(items):
        return _update_completer_then_render(items, "class:key")

    @staticmethod
    def command_scan(response):
        """
        Render Scan command result.
        see: https://redis.io/commands/scan
        """
        return _render_scan(OutputRender.command_keys, response)

    @staticmethod
    def command_sscan(response):
        return _render_scan(OutputRender.render_members, response)

    @staticmethod
    def command_zscan(response):
        return _render_scan(OutputRender.render_members, response)

    @staticmethod
    def command_hscan(response):
        return _render_scan(OutputRender.render_hash_pairs, response)

    @staticmethod
    def command_hkeys(response):
        return _update_completer_then_render(response, "class:field")

    @staticmethod
    def default_render(text):
        pass


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


def _render_scan(render_response, response):
    cursor, responses = response
    if config.raw:
        return b"\n".join([cursor, render_response(responses)])

    rendered = [
        ("class:type", "(cursor) "),
        ("class:integer", cursor.decode()),
        ("", "\n"),
    ]
    rendered_keys = render_response(responses)
    return FormattedText(rendered + rendered_keys)


def _render_pair(pairs, indent):
    keys = [item for item in pairs[::2]]
    values = [item for item in pairs[1::2]]
    rendered = []
    for key, value in zip(keys, values):
        key = ensure_str(key, decode="utf-8")
        value = ensure_str(value, decode="utf-8")
        rendered.append(("class:string", f"{' '*4*indent}{key}: "))
        if isinstance(value, list):
            rendered.append(NEWLINE_TUPLE)
            rendered.extend(_render_pair(value, indent + 1))
        else:
            rendered.append(("class:value", value))
        rendered.append(NEWLINE_TUPLE)
    return rendered[:-1]  # remove last newline


def _update_completer_then_render(items, style):
    """
    """
    str_items = ensure_str(items)
    double_quoted = double_quotes(str_items)
    rendered = _render_list(items, double_quoted, style)
    if config.raw:
        return rendered
    return FormattedText(rendered)


def _update_completer_then_render_withscores(items):
    if not items:
        return EMPTY_LIST
    str_items = ensure_str(items)

    members = [item for item in str_items[::2]]
    scores = [item for item in str_items[1::2]]
    logger.debug(f"[MEMBERS] {members}")
    logger.debug(f"[SCORES] {scores}")
    # render display
    double_quoted = double_quotes(members)
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


# TODO
# special list render, bzpopmax, key-value pair
