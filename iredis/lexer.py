from typing import Callable, Hashable

from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.base import StyleAndTextTuples
from prompt_toolkit.lexers import Lexer, PygmentsLexer, SimpleLexer
from pygments.lexers.scripting import LuaLexer

from .commands import split_command_args
from .exceptions import InvalidArguments, AmbiguousCommand
from .redis_grammar import CONST, get_command_grammar


def get_lexer_mapping():
    """
    Input command render color with lexer mapping below

    This converts token to styles in style.py
    """
    # pygments token
    # http://pygments.org/docs/tokens/
    lexers_dict = {
        "key": SimpleLexer("class:key"),
        "keys": SimpleLexer("class:key"),
        "newkey": SimpleLexer("class:important-key"),
        "destination": SimpleLexer("class:important-key"),
        "member": SimpleLexer("class:member"),
        "members": SimpleLexer("class:member"),
        "value": SimpleLexer("class:string"),
        "element": SimpleLexer("class:string"),
        "svalue": SimpleLexer("class:string"),
        "values": SimpleLexer("class:string"),
        "lexmin": SimpleLexer("class:string"),
        "lexmax": SimpleLexer("class:string"),
        "bit": SimpleLexer("class:bit"),
        "expiration": SimpleLexer("class:integer"),
        "second": SimpleLexer("class:integer"),
        "millisecond": SimpleLexer("class:integer"),
        "start": SimpleLexer("class:integer"),
        "float": SimpleLexer("class:integer"),
        "end": SimpleLexer("class:integer"),
        # stream id
        "stream_id": SimpleLexer("class:integer"),
        "group": SimpleLexer("class:group"),
        "delta": SimpleLexer("class:integer"),
        "offset": SimpleLexer("class:integer"),
        "count": SimpleLexer("class:integer"),
        "rank": SimpleLexer("class:integer"),
        "index": SimpleLexer("class:index"),
        "clientid": SimpleLexer("class:integer"),
        "password": SimpleLexer("class:password"),
        "min": SimpleLexer("class:integer"),
        "max": SimpleLexer("class:integer"),
        "score": SimpleLexer("class:integer"),
        "timeout": SimpleLexer("class:integer"),
        "position": SimpleLexer("class:integer"),
        "cursor": SimpleLexer("class:integer"),
        "pattern": SimpleLexer("class:pattern"),
        "type": SimpleLexer("class:string"),
        "fields": SimpleLexer("class:field"),
        "field": SimpleLexer("class:field"),
        "sfield": SimpleLexer("class:field"),
        "parameter": SimpleLexer("class:field"),
        "channel": SimpleLexer("class:channel"),
        "double_lua": PygmentsLexer(LuaLexer),
        "single_lua": PygmentsLexer(LuaLexer),
        "command": SimpleLexer("class:command"),
        "approximately": SimpleLexer("class:const"),
        "username": SimpleLexer("class:username"),
    }

    lexers_dict.update({key: SimpleLexer("class:const") for key in CONST})
    return lexers_dict


class IRedisLexer(Lexer):
    """
    Lexer class that can dynamically returns any Lexer.

    :param get_lexer: Callable that returns a :class:`.Lexer` instance.
    """

    def __init__(self) -> None:
        self._current_lexer = self._dummy = SimpleLexer()

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        input_text = document.text

        try:
            command, _ = split_command_args(input_text)
            # compile grammar for this command
            grammar = get_command_grammar(command)
            self._current_lexer = GrammarLexer(grammar, lexers=get_lexer_mapping())
        except (InvalidArguments, AmbiguousCommand):
            self._current_lexer = self._dummy

        return self._current_lexer.lex_document(document)

    def invalidation_hash(self) -> Hashable:
        lexer = self.get_lexer() or self._dummy
        return id(lexer)
