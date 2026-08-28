from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/static", tags=["Static"])

STATIC_DIR = (Path(__file__).resolve().parent.parent.parent / "static").resolve()


@router.get("/{file_path:path}", include_in_schema=False, name="static")
def serve_static_file(file_path: str) -> FileResponse:
    """Plain route instead of app.mount(StaticFiles) - a Mount doesn't match
    when the request path lacks the /api prefix stripped by nginx before
    reaching this app, since FastAPI's root_path="/api" only affects Mount
    matching, not ordinary routes like this one."""
    full_path = (STATIC_DIR / file_path).resolve()
    if not full_path.is_relative_to(STATIC_DIR) or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(full_path)
