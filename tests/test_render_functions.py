from iredis import renders


def test_render_list_index():
    raw = ["hello", "world", "foo"]
    out = renders.render_list(raw)
    assert isinstance(out, str)
    assert "3)" in out
    assert "1)" in out
    assert "4)" not in out


def test_render_list_index_const_width():
    raw = ["hello"] * 100
    out = renders.render_list(raw)
    assert isinstance(out, str)
    assert "  1)" in out
    assert "\n100)" in out

    raw = ["hello"] * 1000
    out = renders.render_list(raw)
    assert "   1)" in out
    assert "\n 999)" in out
    assert "\n1000)" in out

    raw = ["hello"] * 10
    out = renders.render_list(raw)
    assert " 1)" in out
    assert "\n 9)" in out
    assert "\n10)" in out
