import logging
from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
    TransformationInput,
)

from .utils import split_command_args
from .exceptions import InvalidArguments
from .commands_csv_loader import all_commands

logger = logging.getLogger(__name__)


class UserInputCommand:
    """
    User inputted command in real time.

    ``GetCommandProcessor`` update it, and ``BottomToolbar`` read it
    """

    def __init__(self):
        # command will always be upper case
        self.command = None


class GetCommandProcessor(Processor):
    """
    Update Footer display text while user input.
    """

    def __init__(self, command_holder, session):
        # processor will call for internal_refresh, when input_text didn't
        # change, don't run
        self.session = session
        self.command_holder = command_holder

    def apply_transformation(
        self, transformation_input: TransformationInput
    ) -> Transformation:
        input_text = transformation_input.document.text
        try:
            command, _ = split_command_args(input_text, all_commands)
        except InvalidArguments:
            self.command_holder.command = None
        else:
            self.command_holder.command = command.upper()

        return Transformation(transformation_input.fragments)
