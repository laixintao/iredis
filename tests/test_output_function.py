from iredis import output


def test_output_bytes():
    assert output.output_bytes(b"hello world") == r"hello world"
    assert output.output_bytes(b'hello"world') == r"hello\"world"
    assert output.output_bytes(b"hello'world") == r"hello'world"

    assert output.output_bytes(b'"hello\\world"') == '\\"hello\\\\world\\"'

    assert output.output_bytes(b"'\"") == "'\\\""
