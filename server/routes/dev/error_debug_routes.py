from fastapi import APIRouter

router = APIRouter(prefix="/dev/errors", tags=["Dev Errors"])


@router.get("/uncaught")
def raise_uncaught_exception() -> None:
    """Raises an unhandled exception on purpose, so the frontend can test
    how it behaves against a raw 500 (e.g. error boundaries, toasts)."""
    raise RuntimeError("Intentional uncaught exception for frontend testing")
