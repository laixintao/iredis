# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import sys
import click
from .commands import dangerous_commands


class ConfirmBoolParamType(click.ParamType):
    name = "confirmation"

    def convert(self, value, param, ctx):
        if isinstance(value, bool):
            return bool(value)
        value = value.lower()
        if value in ("yes", "y"):
            return True
        elif value in ("no", "n"):
            return False
        self.fail("%s is not a valid boolean" % value, param, ctx)

    def __repr__(self):
        return "BOOL"


BOOLEAN_TYPE = ConfirmBoolParamType()


def is_dangerous(command):
    """
    :return : return True, reason str if command is dangerous;
        return False, None otherwise.
    """
    reason = dangerous_commands.get(command)
    return reason is not None, reason


def prompt(*args, **kwargs):
    """Prompt the user for input and handle any abort exceptions."""
    try:
        return click.prompt(*args, **kwargs)
    except click.Abort:
        return False


def confirm_dangerous_command(upper_command):
    """Check if the query is destructive and prompts the user to confirm.

    Returns:
    * None if the query is non-destructive or we can't prompt the user.
    * True if the query is destructive and the user wants to proceed.
    * False if the query is destructive and the user doesn't want to proceed.

    """
    dangerous, reason = is_dangerous(upper_command)
    prompt_text = f"{reason}.\n" "Do you want to proceed? (y/n)"
    if dangerous and sys.stdin.isatty():
        return prompt(prompt_text, type=BOOLEAN_TYPE)
