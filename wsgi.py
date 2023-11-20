"""Web Server Gateway Interface"""

from src.app import app
from waitress import serve
import dotenv
import os

dotenv.load_dotenv()

# run
if __name__ == "__main__":
    serve(app, port=os.environ.get("PORT") or 5000)
