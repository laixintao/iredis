def test_trasaction_rprompt(local_process):
    local_process.sendline("multi")
    local_process.expect("OK")
    local_process.expect("transaction")

    local_process.sendline("get foo")
    local_process.expect("QUEUED")

    local_process.sendline("EXEC")


def test_trasaction_syntax_error(local_process):
    local_process.sendline("multi")
    local_process.sendline("get foo 1")
    local_process.expect("wrong number of arguments for 'get' command")

    local_process.sendline("EXEC")
    local_process.expect("Transaction discarded because of previous errors.")
