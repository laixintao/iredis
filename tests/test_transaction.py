def test_trasaction_rprompt(onetime_process):
    onetime_process.sendline("multi")
    onetime_process.expect("
