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
    "success": "bg:#222222 #00ff5f bold",
    "error": "bg:#222222 #ff005f bold",
    # colors below copied from mycli project, ~~love~~
    # bottom-toolbar
    "bottom-toolbar": "bg:#222222 #aaaaaa",
    "bottom-toolbar.on": "bg:#222222 #ffffff",
    "bottom-toolbar.off": "bg:#222222 #888888",
    "bottom-toolbar.loaded": "bg:#222222 #44aa44",
    # completion
    "completion-menu.completion.current": "bg:#ffffff #000000",
    "completion-menu.completion": "bg:#008888 #ffffff",
    "completion-menu.meta.completion.current": "bg:#44aaaa #000000",
    "completion-menu.meta.completion": "bg:#448888 #ffffff",
    "completion-menu.multi-column-meta": "bg:#aaffff #000000",
    "scrollbar.arrow": "bg:#003333",
    "scrollbar": "bg:#00aaaa",
    "selected": "#ffffff bg:#6666aa",
    "search": "#ffffff bg:#4444aa",
    "search.current": "#ffffff bg:#44aa44",
    "search-toolbar": "noinherit bold",
    "search-toolbar.text": "nobold",
    "system-toolbar": "noinherit bold",
    "arg-toolbar": "noinherit bold",
    "arg-toolbar.text": "nobold",
}

override_style = Style([("bottom-toolbar", "noreverse")])
STYLE = merge_styles([override_style, Style.from_dict(STYLE_DICT)])
