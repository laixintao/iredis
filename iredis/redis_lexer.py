from pygments.lexer import RegexLexer
from pygments.token import Keyword, Name


class RedisLexer(RegexLexer):
    name = "redis lexer"

    tokens = {
        "root": [
            (r"GET", Keyword, "get"),
        ],
        "get": [
            (r"\w+", Name, "#pop"),
        ],
    }


r = RedisLexer()
result = list(r.get_tokens_unprocessed("GET foo"))
print(result)
