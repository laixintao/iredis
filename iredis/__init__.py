import logging

__version__ = "0.2.12"


logging.basicConfig(
    filename="iredis.log",
    filemode="a",
    format="%(levelname)5s %(message)s",
    level="DEBUG",
)

logger = logging.getLogger(__name__)
logger.info("------ iRedis ------")
