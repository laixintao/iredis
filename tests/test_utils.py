import re
import time
from iredis.utils import timer
from unittest.mock import patch


def test_timer():
    with patch("iredis.utils.logger") as mock_logger:
        timer("foo")
        time.sleep(0.1)
        timer("bar")
        mock_logger.debug.assert_called()
        args, kwargs = mock_logger.debug.call_args
        matched = re.match(r"\[timer (\d)\] (0\.\d+) -> bar", args[0])

        assert matched.group(1) == str(3)
        assert 0.1 <= float(matched.group(2)) <= 0.2

        # --- test again ---
        timer("foo")
        time.sleep(0.2)
        timer("bar")
        mock_logger.debug.assert_called()
        args, kwargs = mock_logger.debug.call_args
        matched = re.match(r"\[timer (\d)\] (0\.\d+) -> bar", args[0])

        assert matched.group(1) == str(5)
        assert 0.2 <= float(matched.group(2)) <= 0.3
