# flake8: noqa
from enum import Enum

from sly import Lexer, Parser


class QUOTE(Enum):
    START = 0
    END = 1


class IRedisLexer(Lexer):
    tokens = {ID, QUOTE, ESCAPE, SPACE}

    QUOTE = r"['\"]"
    ESCAPE = r"\\"
    SPACE = r"\s"
    ID = r"[^'\"\\\s]+"


class IRedisParser(Parser):
    tokens = IRedisLexer.tokens

    precedence = (
        ("right", "ESCAPE"),
        # ("left", "ESCAPE", "QUOTE"),
        # ("left", "SPACE"),
    )

    """
    ending: factors

    factors : factors factor
            | factor
            | factors escapes
            | escapes

    escapes : ESCAPE factor
            | ESCAPE QUOTE
            | ESCAPE ESCAPE
            | ESCAPE empty
            | QUOTE

    factor : ID
           | SPACE
    """

    def __init__(self):
        super().__init__()
        self.current_quote = None

    @_("factors")
    def ending(self, p):
        result = []
        buf = []

        stream = iter(p[0])
        for item in stream:
            if item in (" ", None):
                if buf:
                    result.append("".join(buf))
                buf = []
                continue

            if item == QUOTE.START:
                if not buf:
                    buf += [""]
                for next_tok in stream:
                    if next_tok == QUOTE.END:
                        break
                    buf.append(next_tok)

            else:
                buf.append(item)

        if buf:
            result.append("".join(buf))

        return result

    @_("factors factor")
    def factors(self, p):
        return p[0] + [p[1]]

    @_("factor")
    def factors(self, p):
        return [p[0]]

    @_("factors escapes")
    def factors(self, p):
        return p[0] + p[1]

    @_("escapes")
    def factors(self, p):
        return p[0]

    @_("QUOTE")
    def escapes(self, p):
        if self.current_quote is None:
            self.current_quote = p[0]
            return [QUOTE.START]

        if self.current_quote == p[0]:
            self.current_quote = None
            return [QUOTE.END]

        return [p[0]]

    @_("ESCAPE QUOTE")
    def escapes(self, p):
        if self.current_quote is None:
            self.current_quote = p[1]
            return [p[0], QUOTE.START]

        return [p[1]]

    @_("ESCAPE factor")
    def escapes(self, p):
        return [p[0] + p[1]]

    @_("ESCAPE ESCAPE")
    def escapes(self, p):
        if self.current_quote is None:
            return [p[0], p[1]]
        return [p[1]]

    @_("ESCAPE empty")
    def escapes(self, p):
        return [p[1]]

    @_("")
    def empty(self, p):
        return p[-1]

    @_("ID", "SPACE")
    def factor(self, p):
        return p[0]

    def error(self, p):
        if p:
            print("Syntax error at token", p.type)
            # Just discard the token and tell the parser it's okay.
            self.errok()
        else:
            print("Syntax error at EOF")
