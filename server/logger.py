import logging
from logging.handlers import RotatingFileHandler
from server.config import CONFIG
from pathlib import Path

current_dir = Path(__file__).resolve()
log_dir = current_dir.parent.parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "api.log"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

size_handler = RotatingFileHandler(
    log_file,
    maxBytes=CONFIG.log_max_size,
    backupCount=CONFIG.log_backup_count,
)
size_handler.setFormatter(formatter)

if not logger.hasHandlers():
    if CONFIG.debug:
        logger.addHandler(stream_handler)
    logger.addHandler(size_handler)

# LOKI LOGGER
loki_log_file = log_dir / "loki-access-api.log"
loki_access_logger = logging.getLogger("fastapi_access")
loki_access_logger.setLevel(logging.INFO)

# Handler que envia para o arquivo (rotaciona a cada 10MB)
loki_file_handler = RotatingFileHandler(loki_log_file, maxBytes=10485760, backupCount=5)

# Formato do log: [Data] [Nível] [IP] [Método] [Path] [Status]
loki_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s client_ip="%(client_ip)s" method="%(method)s" path="%(path)s" status="%(status_code)s" duration="%(duration).3f" user="%(user)s" email="%(email)s"',
    datefmt="%Y-%m-%d %H:%M:%S",
)
loki_file_handler.setFormatter(loki_formatter)
loki_access_logger.addHandler(loki_file_handler)
