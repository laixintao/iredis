from .config import config, COMPILING_IN_PROGRESS, COMPILING_JUST_FINISH
from .commands_csv_loader import commands_summary
from .utils import command_syntax

BUTTOM_TEXT = "Ctrl-D to exit;"


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
        if config.compiling == COMPILING_IN_PROGRESS:
            anim = self.get_animation_char()
            loading_text = (
                "class:bottom-toolbar.off",
                f"Loading Redis commands {anim}",
            )
            return [loading_text]
        elif config.compiling == COMPILING_JUST_FINISH:
            loading_text = (
                "class:bottom-toolbar.loaded",
                f"Redis commands loaded! Auto Completer activated!",
            )
            return [loading_text]
        else:
            text = BUTTOM_TEXT
            # add command help if valide
            if self.command_holder.command:
                try:
                    command_info = commands_summary[self.command_holder.command]
                    text = command_syntax(self.command_holder.command, command_info)
                except KeyError:
                    pass
        return text
