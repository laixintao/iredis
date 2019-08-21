import re


def output_bytes(b):
    """
    convert bytes to printable text.

    backslash and double-quotes will be escaped by
    backslash.
    "hello\" -> \"hello\\\"

    we don't add outter double quotes here, since
    completer also need this function's return value
    to patch completers.
    
    b'hello' -> "hello"
    b'double"quotes"' -> "double\"quotes\""
    """
    s = str(b)
    s = s[2:-1]  # remove b' '
    # unescape single quote
    s = s.replace(r"\'", "'")
    # escape double quote and backslash
    s = s.replace('"', '\\"')
    return s


def ensure_str(origin, decode=None):
    """
    Ensure is string, for display and completion.
    """
    if isinstance(origin, str):
        return origin
    elif isinstance(origin, list):
        return [ensure_str(b) for b in origin]
    elif isinstance(origin, bytes):
        return output_bytes(origin)
    else:
        raise Exception(f"Unkown type: {type(origin)}, origin: {origin}")
