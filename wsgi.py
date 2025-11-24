import uvicorn
import os

from server.logger import logger

from server.config import CONFIG

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dev = CONFIG.environment == "development"
    logger.info("Starting server...")
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=int(CONFIG.port),
        reload=dev,
        ssl_keyfile=os.path.join(BASE_DIR, "certs", "key.pem") if dev else None,
        ssl_certfile=os.path.join(BASE_DIR, "certs", "cert.pem") if dev else None,
    )
