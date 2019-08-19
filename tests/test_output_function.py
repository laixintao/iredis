from iredis import output


def test_output_bytes():
    output.output_bytes(b"hello world") == "hello world"
    output.output_bytes(b'hello"world') == 'hello"world'
    output.output_bytes(b"hello'world") == "hello'world"
