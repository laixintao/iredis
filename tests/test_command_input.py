def test_wront_select_db_index(local_process):
    local_process.sendline("select 1")
    local_process.expect("OK")

    local_process.sendline("select 128")
    local_process.expect("DB index is out of range")

    local_process.sendline("select abc")
    local_process.expect("invalid DB index")
