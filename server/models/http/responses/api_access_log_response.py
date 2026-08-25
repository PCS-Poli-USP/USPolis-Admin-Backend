from datetime import datetime

from pydantic import BaseModel

from server.models.database.api_access_log_db_model import ApiAccessLog
from server.utils.enums.api_security_level_enum import APISecurityLevel
from server.utils.must_be_int import must_be_int


class ApiAccessLogResponse(BaseModel):
    id: int
    security_level: APISecurityLevel
    endpoint: str
    method: str
    status_code: int
    timestamp: datetime
    ip_address: str | None
    user_agent: str | None
    response_time_ms: int | None
    tags: list[str]
    user_id: int | None
    user_email: str | None = None
    detail: str | None
    request_body: str | None

    @staticmethod
    def from_access_log(access_log: ApiAccessLog) -> "ApiAccessLogResponse":
        return ApiAccessLogResponse(
            id=must_be_int(access_log.id),
            security_level=access_log.security_level,
            endpoint=access_log.endpoint,
            method=access_log.method,
            status_code=access_log.status_code,
            timestamp=access_log.timestamp,
            ip_address=access_log.ip_address,
            user_agent=access_log.user_agent,
            response_time_ms=access_log.response_time_ms,
            tags=access_log.tags,
            user_id=access_log.user_id,
            user_email=access_log.user.email if access_log.user_id else None,
            detail=access_log.detail,
            request_body=access_log.request_body,
        )

    @staticmethod
    def from_access_log_list(
        access_logs: list[ApiAccessLog],
    ) -> list["ApiAccessLogResponse"]:
        return [ApiAccessLogResponse.from_access_log(a) for a in access_logs]
