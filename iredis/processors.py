import logging
from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
    TransformationInput,
)
from prompt_toolkit.contrib.regular_languages.compiler import compile
from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter

from .utils import split_command_args
from .exceptions import InvalidArguments
from .commands_csv_loader import all_commands
from .lexer import lexers_mapping
from .completers import completer_mapping
from .redis_grammar import get_command_grammar

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
        self.last_text = None
        self.session = session
        self.command_holder = command_holder
        self.default_lexer = session.lexer
        self.default_completer = session.completer

    def apply_transformation(
        self, transformation_input: TransformationInput
    ) -> Transformation:
        input_text = transformation_input.document.text
        if input_text != self.last_text and input_text:
            try:
                command, _ = split_command_args(input_text, all_commands)
                VALID_TOKEN = r"""(
                ("([^"]|\\")*?")     |# with double quotes
                ('([^']|\\')*?')     |# with single quotes
                ([^\s"]+)            # without quotes
                )"""
                KEY = fr"(?P<key>{VALID_TOKEN}(\s+{VALID_TOKEN})*)"
                logger.info(f"command is {command}")
                if command == "GET":
                    grammar = compile(
                        fr"(\s*  (?P<command_pattern>(GET))    \s+ {KEY}  \s*)"
                    )

            except InvalidArguments:
                self.command_holder.command = None
                self.session.completer = self.default_completer
                self.session.lexer = self.default_lexer

            else:
                self.command_holder.command = command.upper()
                # compile grammar for this command
                grammar = get_command_grammar(self.command_holder.command)
                lexer = GrammarLexer(grammar, lexers=lexers_mapping)
                completer = GrammarCompleter(grammar, completer_mapping)

                self.session.completer = completer
                self.session.lexer = lexer

            self.last_text = input_text
        return Transformation(transformation_input.fragments)
