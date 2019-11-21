def test_wrong_select_db_index(local_process):
    local_process.sendline("select 1")
    local_process.expect("OK")

    local_process.sendline("select 128")
    local_process.expect("DB index is out of range")

    local_process.sendline("select abc")
    local_process.expect("invalid DB index")

    local_process.sendline("select 15")
    local_process.expect("OK")


def test_set_command_with_shash(clean_redis, local_process):
    local_process.sendline("set a \\hello\\")  # legal redis command
    local_process.expect("OK")

    local_process.sendline("get a")
    local_process.expect(r"hello")
