from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from server.deps.session_dep import SessionDep
from server.models.http.responses.user_session_response import UserSessionResponse
from server.repositories.user_session_repository import UserSessionRepository

embed = Body(..., embed=True)

router = APIRouter(prefix="/sessions/users", tags=["Sessions", "Users"])


@router.get("")
def get_users_sessions(session: SessionDep) -> list[UserSessionResponse]:
    """Get all users sessions"""
    sessions = UserSessionRepository.get_all_sessions(session=session)
    return UserSessionResponse.from_sessions(sessions)


@router.delete("/{session_id}")
def delete_user_session(
    session_id: str,
    session: SessionDep,
) -> JSONResponse:
    """Delete a user session by ID"""
    UserSessionRepository.delete_session(session_id=session_id, session=session)
    session.commit()
    return JSONResponse(content={"message": "Sessão de usuário removida com sucesso."})


@router.delete("/all/{user_id}")
def delete_all_user_session(
    user_id: int,
    session: SessionDep,
) -> JSONResponse:
    """Delete all user sessions by user ID"""
    UserSessionRepository.delete_all_sessions_by_user_id(
        user_id=user_id, session=session
    )
    session.commit()
    return JSONResponse(
        content={"message": "Todas as sessões de usuário removidas com sucesso."}
    )
