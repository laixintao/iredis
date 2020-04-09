import pexpect


def test_start_on_connection_error():
    cli = pexpect.spawn("iredis -p 12345", timeout=1)
    cli.expect("Error 61 connecting to 127.0.0.1:12345. Connection refused.")
    cli.close()
