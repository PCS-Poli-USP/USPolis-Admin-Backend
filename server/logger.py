import logging
from server.config import CONFIG

logger = logging.getLogger()
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("api.log")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

if CONFIG.debug:
    logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)
