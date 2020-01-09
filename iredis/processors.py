import logging
from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
    TransformationInput,
)
from .utils import split_command_args
from .exceptions import InvalidArguments
from .commands_csv_loader import all_commands
from prompt_toolkit.contrib.regular_languages.compiler import compile
from . import redis_grammar
from .config import config
from .redis_grammar import REDIS_COMMANDS, CONST
from .lexer import get_lexer
from .commands_csv_loader import group2commands, commands_summary
from .completers import get_completer

logger = logging.getLogger(__name__)


class UserInputCommand:
    """
    User inputted command in real time.

    ``GetCommandProcessor`` update it, and ``BottomToolbar`` read it
    """

    def __init__(self):
        # command will always be upper case
        self.command = None


default_grammar = compile(redis_grammar.COMMAND)


class GetCommandProcessor(Processor):
    """
    Update Footer display text while user input.
    """

    def __init__(self, command_holder, session):
        self.last_text = None
        self.session = session
        self.command_holder = command_holder

    # TODO my vim completion has problems with enter choose vim-lsp
    def apply_transformation(
        self, transformation_input: TransformationInput
    ) -> Transformation:
        input_text = transformation_input.document.text
        if input_text != self.last_text:
            try:
                command, _ = split_command_args(input_text, all_commands)
                VALID_TOKEN = r"""(
                ("([^"]|\\")*?")     |# with double quotes
                ('([^']|\\')*?')     |# with single quotes
                ([^\s"]+)            # without quotes
                )"""
                PATTERN = fr"(?P<pattern>{VALID_TOKEN})"
                KEY = fr"(?P<key>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
                logger.info(f"command is {command}")
                if command == "GET":
                    grammar = compile(
                        fr"(\s*  (?P<command_pattern>(GET))    \s+ {KEY}  \s*)"
                    )
                else:
                    grammar = default_grammar

            except InvalidArguments:
                self.command_holder.command = None
                grammar = default_grammar

            else:
                self.command_holder.command = command.upper()
            # get lexer
            lexer = get_lexer(group2commands.keys(), grammar)
            # get completer
            completer = get_completer(group2commands, grammar)

            self.session.completer = completer
            self.session.lexer = lexer

            self.last_text = input_text
        return Transformation(transformation_input.fragments)
