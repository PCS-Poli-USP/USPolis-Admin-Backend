from datetime import datetime
from pydantic import BaseModel

from server.models.database.api_access_log import APIAccessLog


class APIAccessLogResponse(BaseModel):
    security_level: str
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    ip_address: str | None
    response_time_ms: float
    tags: list[str]
    user_agent: str
    username: str | None = None
    user_email: str | None = None

    @staticmethod
    def from_db_model(access: APIAccessLog) -> "APIAccessLogResponse":
        return APIAccessLogResponse(
            security_level=access.security_level,
            endpoint=access.endpoint,
            method=access.method,
            status_code=access.status_code,
            timestamp=access.timestamp,
            ip_address=access.ip_address,
            response_time_ms=access.response_time_ms,
            tags=access.tags,
            user_agent=access.user_agent,
            username=access.user.name if access.user else None,
            user_email=access.user.email if access.user else None,
        )

    @staticmethod
    def from_db_model_list(
        access_list: list[APIAccessLog],
    ) -> list["APIAccessLogResponse"]:
        return [APIAccessLogResponse.from_db_model(access) for access in access_list]
