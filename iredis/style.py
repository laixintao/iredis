
from prompt_toolkit.styles import Style

STYLE_DICT = {
    # User input (default text).
    "": "",
    # Prompt.
    "hostname": "",
    "key": "#33aa33",
    "integer": "#ff0000",
    "trailing-input": "bg:#662222 #ffffff",
    "password": "hidden",
}

STYLE = Style.from_dict(STYLE_DICT)
