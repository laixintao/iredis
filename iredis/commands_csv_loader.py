import csv
import json
import copy
from .utils import timer
from . import project_path


def load_command_summary():
    commands_json_path = project_path / "commands.json"

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
    syntax_path = project_path / "command_syntax.csv"

    group = {}
    first_line = True
    command2callback = {}
    with open(syntax_path) as command_syntax:
        csvreader = csv.reader(command_syntax)
        for line in csvreader:
            if first_line:
                first_line = False
                continue
            syntax, command, syntax, func_name = line
            group.setdefault(syntax, []).append(command)
            command2callback[command] = func_name

    group2commands = copy.deepcopy(group)

    # add lowercase commands
    group2command_res = {}
    for syntax in group.keys():
        commands = group[syntax]
        lower_commands = [command.lower() for command in commands]
        commands += lower_commands
        # Space in command cloud be mutiple spaces
        re_commands = [command.replace(" ", r"\s+") for command in commands]
        group2command_res[syntax] = "|".join(re_commands)

    return group2commands, group2command_res, command2callback


timer("[Loader] Start loading commands file...")
group2commands, group2command_res, command2callback = load_command()
# all redis command strings, in UPPER case
# NOTE: Must sort by length, to match longest command first
all_commands = sorted(
    list(command2callback.keys()) + ["HELP"] + ["HELP"],
    key=lambda x: len(x),
    reverse=True,
)
commands_summary = load_command_summary()
timer("[Loader] Finished loading commands.")
