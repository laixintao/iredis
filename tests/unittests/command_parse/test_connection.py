def test_auth(judge_command):
    judge_command("auth 123", {"command": "auth", "password": "123"})


def test_echo(judge_command):
    judge_command("echo hello", {"command": "echo", "message": "hello"})


def test_ping(judge_command):
    judge_command("ping hello", {"command": "ping", "message": "hello"})
    judge_command("ping", {"command": "ping", "message": None})
    judge_command("ping hello world", None)


def test_select(judge_command):
    for index in range(16):
        judge_command(f"select {index}", {"command": "select", "index": str(index)})
    for index in range(16, 100):
        judge_command(f"select {index}", None)
    judge_command("select acb", None)


def test_swapdb(judge_command):
    for index1 in range(16):
        for index2 in range(16):
            judge_command(
                f"swapdb {index1} {index2}",
                {"command": "swapdb", "index": [str(index1), str(index2)]},
            )
    judge_command("swapdb abc 1", None)
    judge_command("swapdb 1", None)


def test_client_caching(judge_command):
    judge_command("CLIENT CACHING YES", {"command": "CLIENT CACHING", "yes": "YES"})
    judge_command("CLIENT CACHING   NO", {"command": "CLIENT CACHING", "yes": "NO"})
    judge_command("CLIENT CACHING", None)
    judge_command("CLIENT CACHING abc", None)
