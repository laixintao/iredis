import os
import logging
from pathlib import Path

__version__ = "0.5.0"


logging.basicConfig(
    filename="iredis.log",
    filemode="a",
    format="%(levelname)5s %(message)s",
    level="DEBUG",
)

logger = logging.getLogger(__name__)
logger.info("------ iRedis ------")
project_path = Path(os.path.dirname(os.path.abspath(__file__))) / "data"
