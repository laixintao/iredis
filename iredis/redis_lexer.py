from pygments.lexer import RegexLexer
from pygments.token import Keyword, Name, Whitespace


class RedisLexer(RegexLexer):
    name = "redis lexer"

    tokens = {
        "root": [(r"\s+", Whitespace), (r"(?i)GET", Keyword, "get")],
        "get": [(r"\s+", Whitespace), (r"\w+", Name, "#pop")],
    }


r = RedisLexer()
result = list(r.get_tokens_unprocessed("GET foo"))
print(result)

result = list(r.get_tokens_unprocessed("get foo"))
print(result)

result = list(r.get_tokens_unprocessed(" get foo"))
print(result)
