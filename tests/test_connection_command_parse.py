def test_auth(judge_command):
    judge_command("auth 123", {"command_password": "auth", "password": "123"})


def test_echo(judge_command):
    judge_command("echo hello", {"command_message": "echo", "message": "hello"})


def test_ping(judge_command):
    judge_command("ping hello", {"command_messagex": "ping", "message": "hello"})
    judge_command("ping", {"command_messagex": "ping", "message": None})
    judge_command("ping hello world", None)


def test_select(judge_command):
    for index in range(16):
        judge_command(
            f"select {index}", {"command_index": "select", "index": str(index)}
        )
    for index in range(16, 100):
        judge_command(f"select {index}", None)
    judge_command("select acb", None)


def test_swapdb(judge_command):
    for index1 in range(16):
        for index2 in range(16):
            judge_command(
                f"swapdb {index1} {index2}",
                {"command_index_index": "swapdb", "index": [str(index1), str(index2)]},
            )
    judge_command("swapdb abc 1", None)
    judge_command("swapdb 1", None)
