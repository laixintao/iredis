def test_pfmerge(judge_command):
    judge_command(
        "PFMERGE hll3 hll1 hll2",
        {"command": "PFMERGE", "newkey": "hll3", "keys": "hll1 hll2"},
    )
