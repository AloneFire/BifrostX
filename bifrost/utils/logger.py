from loguru import logger
from bifrost.config import Config
import sys

logger.remove()

if Config.DEBUG:
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - "
        "<level>{level}</level> - "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.debug("DEBUG MODE: TRUE")
else:
    logger.add(
        sys.stderr,
        level="WARNING",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - "
        "<level>{level}</level> - "
        "<level>{message}</level>",
    )
