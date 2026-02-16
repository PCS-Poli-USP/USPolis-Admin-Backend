from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from server.deps.authenticate import health_token_authenticate
from server.deps.session_dep import SessionDep

router = APIRouter(
    prefix="/health", tags=["Health"], dependencies=[Depends(health_token_authenticate)]
)


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/database")
def database_health_check(session: SessionDep) -> dict[str, str]:
    try:
        session.exec(text("SET statement_timeout = 1000"))  # type: ignore
        session.exec(text("SELECT 1"))  # type: ignore
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {"database": "up"}
