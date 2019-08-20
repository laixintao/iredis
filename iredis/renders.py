"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response, completers: GrammarCompleter) -> formatted result(str)
"""
import logging
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import to_formatted_text, FormattedText

from .output import output_bytes, ensure_str
from .style import STYLE_DICT
from .config import config

logger = logging.getLogger(__name__)


def render_dict(pairs, completers=None):
    for k, v in pairs.items():
        print(k)
        print(v)


def simple_string_reply(text, style=None):
    if isinstance(text, bytes):
        text = output_bytes(text)
    text = f'"{text}"'
    return FormattedText([("", text)])


def render_int(value, completers=None):
    return value


def render_list(byte_items, str_items, style=None):
    if config.raw:
        return b"\n".join(byte_items )
    index_width = len(str(len(str_items)))
    rendered = []
    for index, item in enumerate(str_items):
        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        text = f' "{item}"\n'
        rendered.append((style, text))
    return FormattedText(rendered)


def command_keys(items, completer):
    str_items = ensure_str(items)

    # update completers
    if completer:
        completer.completers["key"] = WordCompleter(str_items)
        completer.completers["keys"] = WordCompleter(str_items)
        logger.debug(f"[Completer] key completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")

    # render is render, completer is completer
    # render and completer are in same function but code are splitted.
    # Give back to Ceasar what is Ceasar's and to God what is God's.
    rendered = render_list(items, str_items, STYLE_DICT["key"])
    return rendered


def render_ok(text, completer):
    """
    If response is b'OK', render ok with success color.
    else render message with Error color.
    """
    text = ensure_str(text)
    if text == "OK":
        return FormattedText([(STYLE_DICT["success"], text)])
    return FormattedText([(STYLE_DICT["error"], text)])
