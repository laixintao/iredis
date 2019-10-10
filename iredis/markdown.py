"""
Markdown render.

use https://github.com/lepture/mistune render to html, then print with my style.
"""

import mistune


class TerminalRender(mistune.Renderer):
    pass


renderer = TerminalRender()
markdown_render = mistune.Markdown(renderer=renderer)
