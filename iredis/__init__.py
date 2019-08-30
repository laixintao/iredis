import logging

__version__ = "0.1.18"


logging.basicConfig(
    filename="iredis.log",
    filemode="a",
    format="%(levelname)5s %(message)s",
    level="DEBUG",
)

logger = logging.getLogger(__name__)
logger.info("------ iRedis ------")
