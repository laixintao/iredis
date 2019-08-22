import re
import time
import logging
from iredis.exceptions import InvalidArguments


logger = logging.getLogger(__name__)

_last_timer = time.time()
_timer_counter = 0
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


def _valide_token(words):
    token = "".join(words).strip()
    if token:
        yield token


def _strip_quote_args(s):
    """
    Given string s, split it into args.(Like bash paring)
    Handle with all quote cases.

    Raise ``InvalidArguments`` if quotes not match

    :return: args list.
    """
    sperator = re.compile(r"\s")
    word = []
    in_quote = None
    pre_back_slash = False
    for char in s:
        if in_quote:
            # close quote
            if char == in_quote:
                if not pre_back_slash:
                    yield from _valide_token(word)
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
                    yield from _valide_token(word)
                    word = []
                else:
                    word.append(char)
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
        yield from _valide_token(word)
    # quote not close
    if in_quote:
        raise InvalidArguments()


def split_command_args(command, all_commands):
    """
    Split Redis command text into command and args.

    :param command: redis command string, with args
    :param all_commands: full redis commands list
    """
    upper_raw_command = command.upper()
    for command_name in all_commands:
        if re.match(r"\s*{}( .*)?$".format(command_name), upper_raw_command):
            l = len(command_name)
            input_command = command[:l]
            input_args = command[l:]
            break
    else:
        raise InvalidArguments(r"`{command} is not a valide Redis Command")

    args = list(_strip_quote_args(input_args))

    logger.debug(f"[Parsed comamnd name] {input_command}")
    logger.debug(f"[Parsed comamnd args] {args}")
    return input_command, args
