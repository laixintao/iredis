import time
import logging


logger = logging.getLogger(__name__)

_last_timer = time.time()
logger.debug(f"[timer] start on {_last_timer}")


def timer(title):
    global _last_timer
    _last_timer = time.time()
    now = time.time()
    tick = now - _last_timer
    _last_timer = now
    logger.debug(f"[timer] {tick} -> {title}")
