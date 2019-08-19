def output_bytes(b):
    """
    convert bytes to printable text.
    
    b'hello' -> "hello"
    b'double"quotes"' -> "double\"quotes\""
    """
    s = str(b)
    s = s[2:-1]  # remove b' '
    return s


def ensure_str(origin):
    if isinstance(origin, list):
        return [ensure_str(b) for b in origin]
    elif isinstance(origin, bytes):
        return output_bytes(origin)
    else:
        raise Exception(f"Unkown type: {type(origin)}, origin: {origin}")
