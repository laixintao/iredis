from iredis.warning import is_dangerous


def test_is_dangerous():
    assert is_dangerous("KEYS") == (True, "KEYS is dangerous, use SCAN instead")
