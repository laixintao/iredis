import time
import threading
from unittest.mock import MagicMock
from iredis.entry import compile_grammar_bg


def test_get_ctrl_C():
    pass


def test_get_ctrl_D():
    pass


def test_patch_grammer_and_session_after_startup():
    session = MagicMock()
    normal_thread_count = threading.active_count()
    session.lexer = None
    session.completer = None
    compile_grammar_bg(session)
    assert session.lexer is None
    assert session.completer is None
    assert threading.active_count() == normal_thread_count + 1

    while threading.active_count() > normal_thread_count:
        time.sleep(0.1)
    assert session.lexer
    assert session.completer
