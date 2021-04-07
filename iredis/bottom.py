import logging
from .commands import commands_summary
from .utils import command_syntax

BUTTOM_TEXT = "Ctrl-D to exit;"
logger = logging.getLogger(__name__)


class BottomToolbar:
    CHAR = "⣾⣷⣯⣟⡿⢿⣻⣽"

    def __init__(self, command_holder):
        self.index = 0
        # BottomToolbar can only read this variable
        self.command_holder = command_holder

    def get_animation_char(self):
        animation = self.CHAR[self.index]

        self.index += 1
        if self.index == len(self.CHAR):
            self.index = 0
        return animation

    def render(self):
        text = BUTTOM_TEXT
        # add command help if valid
        if self.command_holder.command:
            try:
                command_info = commands_summary[self.command_holder.command]
                text = command_syntax(self.command_holder.command, command_info)
            except KeyError as e:
                logger.exception(e)

        return text
