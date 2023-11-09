from loguru import logger
from bifrostx.config import Config
import sys

logger.remove()


logger.add(
    sys.stderr,
    level=Config.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - "
    "<level>{level}</level> - "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
