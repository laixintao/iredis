from prompt_toolkit.styles import Style, merge_styles

override_style = Style([("bottom-toolbar", "noreverse")])

style = REDIS_TOKEN = {
    "key": "#33aa33",
    "important-key": "#058B06",
    "pattern": "bold #33aa33",
    "string": "#FD971F",
    "member": "#FD971F",
    "command": "bold #008000",
    "integer": "#AE81FF",
    "start": "#AE81FF",  # TODO auto merge with integer
    "end": "#AE81FF",
    "const": "bold #AE81FF",
    "time": "#aa22ff",
    "double": "#bb6688",
    "nil": "#808080",
    "bit": "#8541FF",
    "field": "cyan",
}

DOC = {
    "doccommand": "bold",
    "dockey": "#E6DB74",
    "code": "#aaaaaa",
    "h2": "bold #33aa33",
}

GROUP = {
    "group.cluster": "#E6DB74",
    "group.connection": "#E6DB74",
    "group.generic": "#E6DB74",
    "group.geo": "#E6DB74",
    "group.hash": "#E6DB74",
    "group.hyperloglog": "#E6DB74",
    "group.list": "#E6DB74",
    "group.pubsub": "#E6DB74",
    "group.server": "#E6DB74",
    "group.set": "#E6DB74",
    "group.sortedset": "#E6DB74",
    "group.stram": "#E6DB74",
    "group.string": "#E6DB74",
    "group.transections": "#E6DB74",
}


STYLE_DICT = {
    # User input (default text).
    "": "",
    # Prompt.
    "rprompt": "bg:#ff0066 #ffffff",
    "hostname": "",
    "index": "#ff0000",
    "trailing-input": "bg:#ff0000 #000000",
    "password": "hidden",
    "success": "#00ff5f bold",
    "queued": "#32CD32 bold",
    "error": "#ff005f bold",
    "type": "#888",
    # colors below copied from mycli project, ~~love~~
    # bottom-toolbar
    "bottom-toolbar": "bg:#222222 #aaaaaa",
    "bottom-toolbar.on": "bg:#222222 #ffffff",
    "bottom-toolbar.off": "bg:#222222 #888888",
    "bottom-toolbar.loaded": "bg:#222222 #44aa44",
    "bottom-toolbar.since": "bg:#222222 #bc7a00",
    "bottom-toolbar.complexity": "bg:#222222 #666666",
    "bottom-toolbar.group": "bg:#222222 #d2413a bold",
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

BOTTOM_TOOLBAR_TOKEN = {
    # redis token
    f"bottom-toolbar.{token}": f"bg:#222222 {token_style}"
    for token, token_style in REDIS_TOKEN.items()
}

style.update(STYLE_DICT)
style.update(BOTTOM_TOOLBAR_TOKEN)
style.update(DOC)


STYLE = merge_styles([override_style, Style.from_dict(style)])
