import csv
import json

from .utils import timer
from . import project_data


def load_command_summary():
    commands_json_path = project_data / "commands.json"

    with open(commands_json_path) as jsonfile:
        commands_summary = json.load(jsonfile)
    return commands_summary


def load_command():
    """
    load command informations from file.
    :returns:
        - original_commans: dict, command name : Command
        - command_group: dict, group_name: command_names
    """
    syntax_path = project_data / "command_syntax.csv"

    first_line = True
    command2callback = {}
    command2syntax = {}
    groups = {}
    with open(syntax_path) as command_syntax:
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


def load_dangerous():
    """
    Load dangerous commands from csv file.
    """
    first_line = True
    dangerous_file_path = project_data / "dangerous_commands.csv"
    dangerous_command = {}
    with open(dangerous_file_path) as dangerous_file:
        csvreader = csv.reader(dangerous_file)
        for line in csvreader:
            if first_line:
                first_line = False
                continue
            command, reason = line
            dangerous_command[command] = reason
    return dangerous_command


timer("[Loader] Start loading commands file...")
command2callback, command2syntax, groups = load_command()
# all redis command strings, in UPPER case
# NOTE: Must sort by length, to match longest command first
all_commands = sorted(
    list(command2callback.keys()) + ["HELP"], key=lambda x: len(x), reverse=True
)
commands_summary = load_command_summary()
timer("[Loader] Finished loading commands.")
dangerous_commands = load_dangerous()
