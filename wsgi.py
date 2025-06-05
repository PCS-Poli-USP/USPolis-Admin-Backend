import uvicorn

from server.logger import logger

from server.config import CONFIG

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run("server.app:app", host="0.0.0.0", port=int(CONFIG.port), reload=True)
