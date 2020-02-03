from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer
from pygments.lexers.scripting import LuaLexer

from .redis_grammar import CONST, command_grammar


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
        "sstart": SimpleLexer("class:integer"),
        "send": SimpleLexer("class:integer"),
        "delta": SimpleLexer("class:integer"),
        "offset": SimpleLexer("class:integer"),
        "count": SimpleLexer("class:integer"),
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
        "parameter": SimpleLexer("class:field"),
        "channel": SimpleLexer("class:channel"),
        "double_lua": PygmentsLexer(LuaLexer),
        "single_lua": PygmentsLexer(LuaLexer),
        "command": SimpleLexer("class:command"),
    }

    lexers_dict.update({key: SimpleLexer("class:const") for key in CONST})
    return lexers_dict


lexers_mapping = get_lexer_mapping()
default_lexer = GrammarLexer(command_grammar, lexers=lexers_mapping)
