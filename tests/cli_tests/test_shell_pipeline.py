import pexpect


def test_running_disable_shell_pipeline():
    cli = pexpect.spawn("iredis -n 15 --no-shell", timeout=2)
    cli.expect("127.0.0.1")
    cli.sendline("set foo hello")
    cli.expect("OK")
    cli.sendline("get foo | grep w")
    cli.expect(r"hello")
    cli.close()
