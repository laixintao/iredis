import pytest
from unittest.mock import patch
from click.testing import CliRunner

from iredis.entry import gather_args


@pytest.mark.parametrize(
    "is_tty,raw_arg_is_raw,final_config_is_raw",
    [
        (True, None, False),
        (True, True, True),
        (True, False, False),
        (False, None, True),
        (False, True, True),
        (False, False, False),
    ],
)
def test_command_entry_tty(is_tty, raw_arg_is_raw, final_config_is_raw):
    # is tty + raw -> raw
    with patch("sys.stdout.isatty") as patch_tty:
        from iredis.config import config
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
