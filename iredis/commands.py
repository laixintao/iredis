import re
import csv
import json
import logging
import functools
from importlib_resources import read_text, open_text

from .utils import timer, strip_quote_args
from .exceptions import InvalidArguments, AmbiguousCommand
from . import data as project_data


logger = logging.getLogger(__name__)


def _load_command_summary():
    commands_summary = json.loads(read_text(project_data, "commands.json"))
    return commands_summary


def _load_command():
    """
    load command informations from file.
    :returns:
        - original_commans: dict, command name : Command
        - command_group: dict, group_name: command_names
    """
    first_line = True
    command2callback = {}
    command2syntax = {}
    groups = {}
    with open_text(project_data, "command_syntax.csv") as command_syntax:
        csvreader = csv.reader(command_syntax)
        for line in csvreader:
            if first_line:
                first_line = False
                continue
            group, command, syntax, func_name = line
            command2callback[command] = func_name
            command2syntax[command] = syntax
            groups.setdefault(group, []).append(command)

    return command2callback, command2syntax, groups


def _load_dangerous():
    """
    Load dangerous commands from csv file.
    """
    first_line = True
    dangerous_command = {}
    with open_text(project_data, "dangerous_commands.csv") as dangerous_file:
        csvreader = csv.reader(dangerous_file)
        for line in csvreader:
            if first_line:
                first_line = False
                continue
            command, reason = line
            dangerous_command[command] = reason
    return dangerous_command


timer("[Loader] Start loading commands file...")
command2callback, command2syntax, groups = _load_command()
# all redis command strings, in UPPER case
# NOTE: Must sort by length, to match longest command first
all_commands = sorted(
    list(command2callback.keys()) + ["HELP"], key=lambda x: len(x), reverse=True
)
# load commands information from redis-doc/commands.json
commands_summary = _load_command_summary()
# add iredis' commands' summary
commands_summary.update(
    {
        "HELP": {
            "summary": "Show documents for a Redis command.",
            "complexity": "O(1).",
            "arguments": [{"name": "command", "type": "string"}],
            "since": "1.0",
            "group": "iredis",
        },
        "CLEAR": {
            "summary": "Clear the screen like bash clear.",
            "complexity": "O(1).",
            "since": "1.0",
            "group": "iredis",
        },
        "EXIT": {
            "summary": "Exit iredis.",
            "complexity": "O(1).",
            "since": "1.0",
            "group": "iredis",
        },
        "PEEK": {
            "summary": "Get the key's type and value.",
            "arguments": [{"name": "key", "type": "key"}],
            "complexity": "O(1).",
            "since": "1.0",
            "group": "iredis",
        },
    }
)
timer("[Loader] Finished loading commands.")
dangerous_commands = _load_dangerous()


@functools.lru_cache(maxsize=2048)
def split_command_args(command):
    """
    Split Redis command text into command and args.

    :param command: redis command string, with args
    """
    global all_commands

    command = command.strip()
    for command_name in all_commands:
        # for command that is paritaly inputed, like `command in`, we should
        # match with `command info`, otherwise, `command in` will result in
        # `command` with `args` is ('in') which is an invalid case.
        normalized_input_command = " ".join(command.split()).upper()
        if (
            re.search("\s", command)
            and command_name.startswith(normalized_input_command)
            and command_name != normalized_input_command
        ):
            raise AmbiguousCommand("command is not finished")
        # allow multiplt space in user inputed command
        command_allow_multi_spaces = "[ ]+".join(command_name.split())
        matcher = re.match(fr"({command_allow_multi_spaces})( |$)", command.upper())
        if matcher:
            matched_command_len = len(matcher.group(1))
            input_command = command[:matched_command_len]
            input_args = command[matcher.end() :]
            break
    else:
        raise InvalidArguments(f"`{command}` is not a valid Redis Command")

    args = list(strip_quote_args(input_args))

    return input_command, args


def split_unknown_args(command):
    """
    Split user's input into command and args.
    """
    command = command.strip()
    input_command, *input_args = command.split(" ")
    return input_command, list(strip_quote_args(" ".join(input_args)))
