import logging
from server.config import CONFIG
from pathlib import Path

current_dir = Path(__file__).resolve()
log_dir = current_dir.parent.parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "api.log"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

if not logger.hasHandlers():
    if CONFIG.debug:
        logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

