import pytest
from unittest.mock import patch

from iredis.entry import gather_args, parse_url, DSN


@pytest.mark.parametrize(
    "is_tty,raw_arg_is_raw,final_config_is_raw",
    [
        (True, None, False),
        (True, True, True),
        (True, False, False),
        (False, None, True),
        (False, True, True),
        (False, False, True),  # not tty
    ],
)
def test_command_entry_tty(is_tty, raw_arg_is_raw, final_config_is_raw, config):
    # is tty + raw -> raw
    with patch("sys.stdout.isatty") as patch_tty:

        patch_tty.return_value = is_tty
        if raw_arg_is_raw is None:
            call = ["iredis"]
        elif raw_arg_is_raw is True:
            call = ["iredis", "--raw"]
        elif raw_arg_is_raw is False:
            call = ["iredis", "--no-raw"]
        else:
            raise Exception()
        gather_args.main(call, standalone_mode=False)
        assert config.raw == final_config_is_raw


def test_command_with_decode_utf_8():
    from iredis.config import config

    gather_args.main(["iredis", "--decode", "utf-8"], standalone_mode=False)
    assert config.decode == "utf-8"

    gather_args.main(["iredis"], standalone_mode=False)
    assert config.decode == ""


@pytest.mark.parametrize(
    "url,dsn",
    [
        (
            "redis://localhost:6379/3",
            DSN(
                scheme="redis",
                host="localhost",
                port=6379,
                path=None,
                db=3,
                username=None,
                password=None,
            ),
        )
    ],
)
def test_parse_url(url, dsn):
    assert parse_url(url) == dsn
    # TODO more on www.iana.org/assignments/uri-schemes/prov/redis
