from fastapi import APIRouter, Body
from sqlmodel import col, select

from server.deps.session_dep import SessionDep
from server.models.database.api_access_log import APIAccessLog
from server.models.http.responses.api_access_log_response import APIAccessLogResponse

embed = Body(..., embed=True)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/logs")
def get_api_access_logs(session: SessionDep) -> list[APIAccessLogResponse]:
    """
    Retrieve API access logs for analytics.

    Returns:
        APIAnalyticsResponse: An object containing analytics data.
    """
    # Implementation would go here
    statement = select(APIAccessLog).order_by(col(APIAccessLog.timestamp).desc())
    logs = list(session.exec(statement).all())
    return APIAccessLogResponse.from_db_model_list(logs)
