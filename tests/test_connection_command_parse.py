def test_auth(judge_command):
    judge_command("auth 123", {"command_password": "auth", "password": "123"})
