
from prompt_toolkit.styles import Style

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
}

STYLE = Style.from_dict(STYLE_DICT)
