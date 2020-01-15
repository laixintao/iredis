from iredis.entry import write_result


def test_when_using_decode(config, capfd):
    config.decode = "utf-8"
    config.raw = True
    write_result("你好")

    out, err = capfd.readouterr()
    assert out == "你好\n"
