def test_set(local_process):
    local_process.sendline("set foo bar")
    local_process.expect("OK")

    local_process.sendline("set foo bar nx")
    local_process.expect("(nil)")

    local_process.sendline("set foo bar xx")
    local_process.expect("OK")

    local_process.sendline("set foo1 bar xx")
    local_process.expect("(nil)")
