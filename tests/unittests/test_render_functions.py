import os
import time
from prompt_toolkit.formatted_text import FormattedText
from iredis import renders
from iredis.config import config
from iredis.completers import IRedisCompleter


def strip_formatted_text(formatted_text):
    return "".join(text[1] for text in formatted_text)


def test_render_simple_string_raw_using_raw_render():
    assert renders.OutputRender.render_raw(b"OK") == b"OK"
    assert renders.OutputRender.render_raw(b"BUMPED 1") == b"BUMPED 1"
    assert renders.OutputRender.render_raw(b"STILL 1") == b"STILL 1"


def test_render_simple_string():
    assert renders.OutputRender.render_simple_string(b"OK") == FormattedText(
        [("class:success", "OK")]
    )
    assert renders.OutputRender.render_simple_string(b"BUMPED 1") == FormattedText(
        [("class:success", "BUMPED 1")]
    )
    assert renders.OutputRender.render_simple_string(b"STILL 1") == FormattedText(
        [("class:success", "STILL 1")]
    )


def test_render_list_index():
    raw = ["hello", "world", "foo"]
    out = renders._render_list([item.encode() for item in raw], raw)
    out = strip_formatted_text(out)
    assert isinstance(out, str)
    assert "3)" in out
    assert "1)" in out
    assert "4)" not in out


def test_render_list_index_const_width():
    raw = ["hello"] * 100
    out = renders._render_list([item.encode() for item in raw], raw)
    out = strip_formatted_text(out)
    assert isinstance(out, str)
    assert "  1)" in out
    assert "\n100)" in out

    raw = ["hello"] * 1000
    out = renders._render_list([item.encode() for item in raw], raw)
    out = strip_formatted_text(out)
    assert "   1)" in out
    assert "\n 999)" in out
    assert "\n1000)" in out

    raw = ["hello"] * 10
    out = renders._render_list([item.encode() for item in raw], raw)
    out = strip_formatted_text(out)
    assert " 1)" in out
    assert "\n 9)" in out
    assert "\n10)" in out


def test_render_list_using_raw_render():
    raw = ["hello", "world", "foo"]
    out = renders.OutputRender.render_raw([item.encode() for item in raw])
    assert b"hello\nworld\nfoo" == out


def test_render_list_with_nil_init():
    raw = [b"hello", None, b"world"]
    out = renders.OutputRender.render_list(raw)
    out = strip_formatted_text(out)
    assert out == '1) "hello"\n2) (nil)\n3) "world"'


def test_render_list_with_nil_init_while_config_raw():
    raw = [b"hello", None, b"world"]
    out = renders.OutputRender.render_raw(raw)
    assert out == b"hello\n\nworld"


def test_render_list_with_empty_list_raw():
    raw = []
    out = renders.OutputRender.render_raw(raw)
    assert out == b""


def test_render_list_with_empty_list():
    raw = []
    out = renders.OutputRender.render_list(raw)
    out = strip_formatted_text(out)
    assert out == "(empty list or set)"


def test_ensure_str_bytes():
    assert renders.ensure_str(b"hello world") == r"hello world"
    assert renders.ensure_str(b"hello'world") == r"hello'world"
    assert renders.ensure_str("你好".encode()) == r"\xe4\xbd\xa0\xe5\xa5\xbd"


def test_double_quotes():
    assert renders.double_quotes('hello"world') == r'"hello\"world"'
    assert renders.double_quotes('"hello\\world"') == '"\\"hello\\world\\""'

    assert renders.double_quotes("'") == '"\'"'
    assert renders.double_quotes("\\") == '"\\"'
    assert renders.double_quotes('"') == '"\\""'


def test_render_int():
    config.raw = False
    assert renders.OutputRender.render_int(12) == FormattedText(
        [("class:type", "(integer) "), ("", "12")]
    )


def test_render_int_raw():
    assert renders.OutputRender.render_raw(12) == b"12"


def test_render_list_or_string():
    assert renders.OutputRender.render_list_or_string("") == '""'
    assert renders.OutputRender.render_list_or_string("foo") == '"foo"'
    assert renders.OutputRender.render_list_or_string(
        [b"foo", b"bar"]
    ) == FormattedText(
        [
            ("", "1)"),
            ("", " "),
            ("class:string", '"foo"'),
            ("", "\n"),
            ("", "2)"),
            ("", " "),
            ("class:string", '"bar"'),
        ]
    )


def test_render_list_or_string_nil_and_empty_list():
    assert renders.OutputRender.render_list_or_string(None) == FormattedText(
        [("class:type", "(nil)")]
    )
    assert renders.OutputRender.render_list_or_string([]) == FormattedText(
        [("class:type", "(empty list or set)")]
    )


def test_render_raw_nil_and_empty_list():
    assert renders.OutputRender.render_raw(None) == b""
    assert renders.OutputRender.render_raw([]) == b""


def test_list_or_string():
    config.raw = False
    assert renders.OutputRender.render_string_or_int(b"10.1") == '"10.1"'
    assert renders.OutputRender.render_string_or_int(3) == FormattedText(
        [("class:type", "(integer) "), ("", "3")]
    )


def test_command_keys():
    completer = IRedisCompleter()
    completer.key_completer.words = []
    config.raw = False
    rendered = renders.OutputRender.command_keys([b"cat", b"dog", b"banana"])
    completer.update_completer_for_response("KEYS", None, [b"cat", b"dog", b"banana"])

    assert rendered == FormattedText(
        [
            ("", "1)"),
            ("", " "),
            ("class:key", '"cat"'),
            ("", "\n"),
            ("", "2)"),
            ("", " "),
            ("class:key", '"dog"'),
            ("", "\n"),
            ("", "3)"),
            ("", " "),
            ("class:key", '"banana"'),
        ]
    )
    assert completer.key_completer.words == ["banana", "dog", "cat"]


def test_command_scan():
    completer = IRedisCompleter()
    completer.key_completer.words = []
    config.raw = False
    rendered = renders.OutputRender.command_scan(
        [b"44", [b"a", b"key:__rand_int__", b"dest", b" a"]]
    )
    completer.update_completer_for_response(
        "SCAN", ("0",), [b"44", [b"a", b"key:__rand_int__", b"dest", b" a"]]
    )

    assert rendered == FormattedText(
        [
            ("class:type", "(cursor) "),
            ("class:integer", "44"),
            ("", "\n"),
            ("", "1)"),
            ("", " "),
            ("class:key", '"a"'),
            ("", "\n"),
            ("", "2)"),
            ("", " "),
            ("class:key", '"key:__rand_int__"'),
            ("", "\n"),
            ("", "3)"),
            ("", " "),
            ("class:key", '"dest"'),
            ("", "\n"),
            ("", "4)"),
            ("", " "),
            ("class:key", '" a"'),
        ]
    )
    assert completer.key_completer.words == [" a", "dest", "key:__rand_int__", "a"]


def test_command_sscan():
    completer = IRedisCompleter()
    completer.member_completer.words = []
    rendered = renders.OutputRender.command_sscan(
        [b"44", [b"a", b"member:__rand_int__", b"dest", b" a"]]
    )
    completer.update_completer_for_response(
        "SSCAN", (0), [b"44", [b"a", b"member:__rand_int__", b"dest", b" a"]]
    )

    assert rendered == FormattedText(
        [
            ("class:type", "(cursor) "),
            ("class:integer", "44"),
            ("", "\n"),
            ("", "1)"),
            ("", " "),
            ("class:member", '"a"'),
            ("", "\n"),
            ("", "2)"),
            ("", " "),
            ("class:member", '"member:__rand_int__"'),
            ("", "\n"),
            ("", "3)"),
            ("", " "),
            ("class:member", '"dest"'),
            ("", "\n"),
            ("", "4)"),
            ("", " "),
            ("class:member", '" a"'),
        ]
    )
    assert completer.member_completer.words == [
        " a",
        "dest",
        "member:__rand_int__",
        "a",
    ]


def test_command_sscan_config_raw():
    completer = IRedisCompleter()
    completer.member_completer.words = []
    rendered = renders.OutputRender.render_raw(
        [b"44", [b"a", b"member:__rand_int__", b"dest", b" a"]]
    )
    completer.update_completer_for_response(
        "SSCAN", (0), [b"44", [b"a", b"member:__rand_int__", b"dest", b" a"]]
    )

    assert rendered == b"44\na\nmember:__rand_int__\ndest\n a"
    assert completer.member_completer.words == [
        " a",
        "dest",
        "member:__rand_int__",
        "a",
    ]


def test_render_members():
    completer = IRedisCompleter()
    completer.member_completer.words = []
    config.withscores = True
    resp = [b"duck", b"667", b"camel", b"708"]
    rendered = renders.OutputRender.render_members(resp)
    completer.update_completer_for_response("ZRANGE", ("foo", "0", "-1"), resp)

    assert rendered == FormattedText(
        [
            ("", "1)"),
            ("", " "),
            ("class:integer", "667 "),
            ("class:member", '"duck"'),
            ("", "\n"),
            ("", "2)"),
            ("", " "),
            ("class:integer", "708 "),
            ("class:member", '"camel"'),
        ]
    )
    assert completer.member_completer.words == ["camel", "duck"]


def test_render_members_config_raw():
    completer = IRedisCompleter()
    completer.member_completer.words = []
    config.withscores = True
    resp = [b"duck", b"667", b"camel", b"708"]
    rendered = renders.OutputRender.render_raw(resp)
    completer.update_completer_for_response("ZRANGE", (), resp)

    assert rendered == b"duck\n667\ncamel\n708"
    assert completer.member_completer.words == ["camel", "duck"]


def test_render_unixtime_config_raw():
    # fake the timezone and reload
    os.environ["TZ"] = "Asia/Shanghai"
    time.tzset()
    rendered = renders.OutputRender.render_unixtime(1570469891)

    assert rendered == FormattedText(
        [
            ("class:type", "(integer) "),
            ("", "1570469891"),
            ("", "\n"),
            ("class:type", "(local time)"),
            ("", " "),
            ("", "2019-10-08 01:38:11"),
        ]
    )


def test_render_unixtime():
    rendered = renders.OutputRender.render_raw(1570469891)

    assert rendered == b"1570469891"


def test_bulk_string_reply():
    assert renders.OutputRender.render_bulk_string(b"'\"") == '''"'\\""'''


def test_bulk_string_reply_raw():
    assert renders.OutputRender.render_raw(b"hello") == b"hello"


def test_render_bulk_string_decoded():
    EXPECTED_RENDER = """# Server\nredis_version:5.0.5\nredis_git_sha1:00000000\nredis_git_dirty:0\nredis_build_id:31cd6e21ec924b46"""  # noqa
    _input = b"# Server\r\nredis_version:5.0.5\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:31cd6e21ec924b46"  # noqa
    assert renders.OutputRender.render_bulk_string_decode(_input) == EXPECTED_RENDER


def test_render_bulk_string_decoded_with_decoded_utf8():
    EXPECTED_RENDER = """# Server\nredis_version:5.0.5\nredis_git_sha1:00000000\nredis_git_dirty:0\nredis_build_id:31cd6e21ec924b46"""  # noqa
    _input = "# Server\r\nredis_version:5.0.5\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:31cd6e21ec924b46"  # noqa
    assert renders.OutputRender.render_bulk_string_decode(_input) == EXPECTED_RENDER


def test_render_time():
    value = [b"1571305643", b"765481"]
    assert renders.OutputRender.render_time(value) == FormattedText(
        [
            ("class:type", "(unix timestamp) "),
            ("", "1571305643"),
            ("", "\n"),
            ("class:type", "(millisecond) "),
            ("", "765481"),
            ("", "\n"),
            ("class:type", "(convert to local timezone) "),
            ("", "2019-10-17 17:47:23.765481"),
        ]
    )

    assert renders.OutputRender.render_raw(value) == b"1571305643\n765481"


def test_render_nested_pairs():
    text = [
        b"peak.allocated",
        10160336,
        b"lua.caches",
        0,
        b"db.0",
        [b"overhead.hashtable.main", 648, b"overhead.hashtable.expires", 32],
        b"db.1",
        [b"overhead.hashtable.main", 112, b"overhead.hashtable.expires", 32],
        b"fragmentation",
        b"0.062980629503726959",
        b"fragmentation.bytes",
        -9445680,
    ]

    assert renders.OutputRender.render_raw(text) == (
        b"peak.allocated\n10160336\nlua.caches\n0\ndb.0\noverhead.hashtable.main\n64"
        b"8\noverhead.hashtable.expires\n32\ndb.1\noverhead.hashtable.main\n112\nove"
        b"rhead.hashtable.expires\n32\nfragmentation\n0.062980629503726959\nfragmentat"
        b"ion.bytes\n-9445680"
    )

    assert renders.OutputRender.render_nested_pair(text) == FormattedText(
        [
            ("class:string", "peak.allocated: "),
            ("class:value", "10160336"),
            ("", "\n"),
            ("class:string", "lua.caches: "),
            ("class:value", "0"),
            ("", "\n"),
            ("class:string", "db.0: "),
            ("", "\n"),
            ("class:string", "    overhead.hashtable.main: "),
            ("class:value", "648"),
            ("", "\n"),
            ("class:string", "    overhead.hashtable.expires: "),
            ("class:value", "32"),
            ("", "\n"),
            ("class:string", "db.1: "),
            ("", "\n"),
            ("class:string", "    overhead.hashtable.main: "),
            ("class:value", "112"),
            ("", "\n"),
            ("class:string", "    overhead.hashtable.expires: "),
            ("class:value", "32"),
            ("", "\n"),
            ("class:string", "fragmentation: "),
            ("class:value", "0.062980629503726959"),
            ("", "\n"),
            ("class:string", "fragmentation.bytes: "),
            ("class:value", "-9445680"),
        ]
    )


def test_render_nested_list():
    text = [[b"get", 2, [b"readonly", b"fast"], 1, 1, 1]]
    assert renders.OutputRender.render_list(text) == FormattedText(
        [
            ("", "1)"),
            ("", " "),
            ("", "1)"),
            ("", " "),
            ("class:string", '"get"'),
            ("", "\n"),
            ("", "   "),
            ("", "2)"),
            ("", " "),
            ("class:string", '"2"'),
            ("", "\n"),
            ("", "   "),
            ("", "3)"),
            ("", " "),
            ("", "1)"),
            ("", " "),
            ("class:string", '"readonly"'),
            ("", "\n"),
            ("", "      "),
            ("", "2)"),
            ("", " "),
            ("class:string", '"fast"'),
            ("", "\n"),
            ("", "   "),
            ("", "4)"),
            ("", " "),
            ("class:string", '"1"'),
            ("", "\n"),
            ("", "   "),
            ("", "5)"),
            ("", " "),
            ("class:string", '"1"'),
            ("", "\n"),
            ("", "   "),
            ("", "6)"),
            ("", " "),
            ("class:string", '"1"'),
        ]
    )


def test_render_bytes(config):
    assert renders.OutputRender.render_bytes(b"bytes\n") == b"bytes"


def test_render_bytes_raw(config):
    assert renders.OutputRender.render_raw(b"bytes\n") == b"bytes\n"
