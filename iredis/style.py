
from prompt_toolkit.styles import Style, merge_styles

STYLE_DICT = {
    # User input (default text).
    "": "",
    # Prompt.
    "hostname": "",
    "key": "#33aa33",
    "integer": "#ff0000",
    "trailing-input": "bg:#ff0000 #000000",
    "password": "hidden",
    "success": "#A6E22E",
    "error": "#F92672",
    # bottom-toolbar
    "bottom-toolbar": "bg:#222222 #aaaaaa",
    "bottom-toolbar.on": "bg:#222222 #ffffff",
    "bottom-toolbar.off": "bg:#222222 #888888",
    "bottom-toolbar.loaded": "bg:#222222 #44aa44",
}

override_style = Style([("bottom-toolbar", "noreverse")])
STYLE = merge_styles([override_style, Style.from_dict(STYLE_DICT)])
