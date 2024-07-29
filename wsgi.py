
import uvicorn

from server.app import app

from server.config import CONFIG

if __name__ == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=int(CONFIG.port), reload=True)