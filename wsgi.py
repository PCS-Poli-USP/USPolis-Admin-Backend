"""Web Server Gateway Interface"""

from src.app import app

# run development
if __name__ == "__main__":
  app.run(debug=True)
