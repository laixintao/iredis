"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response, completers: GrammarCompleter) -> formatted result
"""
import logging
from prompt_toolkit.completion import WordCompleter

from .output import output_bytes

logger = logging.getLogger(__name__)


def render_dict(pairs, completers=None):
    for k, v in pairs.items():
        print(k)
        print(v)


def render_int(value, completers=None):
    return value


def render_list(items, style=None):
    # TODO with return type class / style
    rendered = []
    for item in items:
        if isinstance(item, bytes):
            item = output_bytes(item)
        rendered.append(item)
    return rendered


def command_keys(items, completer):
    rendered = render_list(items)
    if completer:
        completer.completers["key"] = WordCompleter(rendered)
        completer.completers["keys"] = WordCompleter(rendered)
        logger.debug(f"[Completer] key completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")
    return rendered
