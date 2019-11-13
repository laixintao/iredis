import logging
from typing import Iterable

from pygments.lexer import RegexLexer
from pygments.token import Keyword, Name, Whitespace
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import Completer, CompleteEvent, Completion
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.document import Document

logger = logging.getLogger(__name__)


class RedisLexer(RegexLexer):
    name = "redis lexer"

    tokens = {
        "root": [(r"\s+", Whitespace), (r"(?i)GET", Keyword, "get")],
        "get": [(r"\s+", Whitespace), (r"\w+", Name, "#pop")],
    }


class RedisCompleter(Completer):
    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """
        Find all text except last word;
        Get all avaiable tokens for last word;
        return WordCompleter, with last word
        """
        return ["hello", "world"]


r = RedisLexer()
# result = list(r.get_tokens_unprocessed("GET foo"))
# print(result)

# result = list(r.get_tokens_unprocessed("get foo"))
# print(result)

# result = list(r.get_tokens_unprocessed(" get foo"))
# print(result)


completer = RedisCompleter()

text = prompt("Enter HTML: ", lexer=PygmentsLexer(RedisLexer), completer=completer)
print("You said: %s" % text)
