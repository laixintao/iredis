import logging

from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
    TransformationInput,
)

from .exceptions import InvalidArguments, AmbiguousCommand
from .commands import split_command_args

logger = logging.getLogger(__name__)


class UserInputCommand:
    """
    User inputted command in real time.

    ``UpdateBottomProcessor`` update it, and ``BottomToolbar`` read it
    """

    def __init__(self):
        # command will always be upper case
        self.command = None


class UpdateBottomProcessor(Processor):
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
            command, _ = split_command_args(input_text)
        except (InvalidArguments, AmbiguousCommand):
            self.command_holder.command = None
        else:
            self.command_holder.command = command.upper()

        return Transformation(transformation_input.fragments)


class PasswordProcessor(Processor):
    """
    Processor that turns masks the input. (For passwords.)

    :param char: (string) Character to be used. "*" by default.
    """

    def __init__(self, char: str = "*") -> None:
        self.char = char

    def apply_transformation(self, ti: TransformationInput) -> Transformation:
        input_text = ti.document.text
        default_transformation = Transformation(ti.fragments)
        try:
            command, _ = split_command_args(input_text)
        except (InvalidArguments, AmbiguousCommand):
            return default_transformation

        if command.upper() != "AUTH":
            return default_transformation

        fragments = []
        for style, text, *handler in ti.fragments:
            if style == "class:password":
                fragments.append((style, self.char * len(text), *handler))
            else:
                fragments.append((style, text, *handler))
        return Transformation(fragments)
