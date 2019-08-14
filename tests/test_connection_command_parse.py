def test_auth(judge_command):
    judge_command("auth 123", {"command_password": "auth", "password": "123"})


def test_echo(judge_command):
    judge_command("echo hello", {"command_message": "echo", "message": "hello"})


def test_ping(judge_command):
    judge_command("ping hello", {"command_messagex": "ping", "message": "hello"})
    judge_command("ping", {"command_messagex": "ping", "message": None})
    judge_command("ping hello world", None)
