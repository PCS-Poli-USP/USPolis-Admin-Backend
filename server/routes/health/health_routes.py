from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

from server.deps.authenticate import health_token_authenticate
from server.deps.session_dep import SessionDep
from server.repositories.user_schedule_repository import UserScheduleRepository

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


@router.post("/user-schedules/invalidate-expired")
def invalidate_expired_user_schedules(session: SessionDep) -> JSONResponse:
    try:
        invalidated_ids = UserScheduleRepository.invalidate_expired_current_schedules(
            session=session
        )
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error while invalidating expired user schedules: {str(exc)}",
        ) from exc

    return JSONResponse(content={"invalidated_ids": invalidated_ids})
