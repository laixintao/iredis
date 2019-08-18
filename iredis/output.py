def output_bytes(b):
    """
    convert bytes to printable text.
    
    b'hello' -> "hello"
    b'double"quotes"' -> "double\"quotes\""
    """
    s = str(b)
    s = s[2:-1]  # remove b' '
    return s
