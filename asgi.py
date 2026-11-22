"""Entry point for gunicorn (`gunicorn asgi:app`)."""

from server.app import app

__all__ = ["app"]
