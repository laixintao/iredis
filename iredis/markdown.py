"""
Markdown render.

use https://github.com/lepture/mistune render to html, then print with my style.
"""

import logging
import mistune
import re
from prompt_toolkit.formatted_text import to_formatted_text, HTML


logger = logging.getLogger(__name__)


class TerminalRender(mistune.HTMLRenderer):
    def _to_title(self, text):
        return f"{text}\n{'='*len(text)}\n"

    def paragraph(self, text):
        return text + "\n\n"

    def block_code(self, code, info=None):
        code = "\n".join(["  " + line for line in code.splitlines()])
        return super().block_code(code)

    def heading(self, text, level):
        if level == 2:
            header_text = self._to_title(text)
            return super().heading(header_text, 2)
        return super().heading(self._to_title(text), level)

    def list(self, body, ordered, *args, **kwargs):
        """Rendering list tags like ``<ul>`` and ``<ol>``.

        :param body: body contents of the list.
        :param ordered: whether this list is ordered or not.
        """
        tag = "ul"
        if ordered:
            tag = "ol"
        return "<{}>{}</{}>\n".format(tag, body, tag)

    def list_item(self, text, *args):
        """Rendering list item snippet. Like ``<li>``."""
        return "<li> * %s</li>\n" % text


renderer = TerminalRender()
markdown_render = mistune.Markdown(renderer)

# replace redis doc's title (and following newlines & spaces)
# with markdown's second level title
redisdoc_title_re = re.compile(r"^@(\w+) *(?:\n+|$)")


def replace_to_markdown_title(original):
    replaced = redisdoc_title_re.sub(r"## \g<1>", original)
    return replaced


def render(text):
    replaced = replace_to_markdown_title(text)
    html_text = markdown_render(replaced)
    logger.debug(f"[Document] {html_text} ..."[:20])
    return to_formatted_text(HTML(html_text))
