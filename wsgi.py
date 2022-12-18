"""Web Server Gateway Interface"""

from src.app import app
from waitress import serve

# run
if __name__ == "__main__":
  serve(app, port=5000)
