"""
Markdown render.

use https://github.com/lepture/mistune render to html, then print with my style.
"""

import mistune
from prompt_toolkit import HTML


class TerminalRender(mistune.Renderer):
    pass


renderer = TerminalRender()
markdown_render = mistune.Markdown(renderer=renderer)


def render(text):
    return HTML(markdown_render(text))
