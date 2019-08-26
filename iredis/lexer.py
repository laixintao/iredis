from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.contrib.regular_languages.lexer import GrammarLexer


def get_lexer(command_groups, redis_grammar):
    """
    Input command render color with lexer mapping below
    """
    # pygments token
    # http://pygments.org/docs/tokens/
    lexers_dict = {
        "key": SimpleLexer("class:key"),
        "keys": SimpleLexer("class:key"),
        "value": SimpleLexer("class:string"),
        "expiration": SimpleLexer("class:integer"),
        "condition": SimpleLexer("class:const"),
        "index": SimpleLexer("class:index"),
        "password": SimpleLexer("class:password"),
    }

    lexers_dict.update({key: SimpleLexer("class:command") for key in command_groups})
    lexer = GrammarLexer(redis_grammar, lexers=lexers_dict)
    return lexer
