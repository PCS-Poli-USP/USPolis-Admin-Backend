"""Request helpers shared by the middlewares (and a few routes)."""

from fastapi import Request
from starlette.types import Scope


def get_client_ip(request: Request) -> str | None:
    # Uvicorn already resolves X-Forwarded-For into `request.client`, trusting
    # it only from --forwarded-allow-ips (Nginx). Reading the header here
    # instead would let any client pick its own IP and dodge per-IP limits.
    return request.client.host if request.client else None


def app_path(scope: Scope) -> str:
    """Request path without the app's root path (e.g. "/api/classrooms" and
    "/classrooms" both become "/classrooms")."""
    path: str = scope.get("path", "")
    root_path: str = scope.get("root_path", "")
    if root_path and (path == root_path or path.startswith(root_path + "/")):
        return path[len(root_path) :] or "/"
    return path
