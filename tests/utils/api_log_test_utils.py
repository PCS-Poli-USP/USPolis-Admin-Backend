"""Shared, DB-free helper for building ApiAccessLog object graphs in pure
unit tests (no session, nothing persisted).

Constructed directly rather than via a ModelFactory - no factory/dict
scaffolding exists for ApiAccessLog yet, and it's only needed by the
api_access_log and api_incident_report response-model tests, so a full
base-dict/model-dict/base-factory/model-factory stack would be pure
overhead. See TESTS.md's "Test data protocol" section before adding a new
make_* helper here."""

from datetime import datetime

from server.models.database.api_access_log_db_model import ApiAccessLog
from server.models.database.user_db_model import User
from server.utils.enums.api_security_level_enum import APISecurityLevel

_next_id = iter(range(1, 1_000_000))


def make_api_access_log(
    *,
    security_level: APISecurityLevel = APISecurityLevel.PUBLIC,
    endpoint: str = "/api/classrooms",
    method: str = "GET",
    status_code: int = 200,
    user: User | None = None,
    tags: list[str] | None = None,
) -> ApiAccessLog:
    log = ApiAccessLog(
        id=next(_next_id),
        security_level=security_level,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        timestamp=datetime(2025, 1, 1, 10, 0),
        ip_address="127.0.0.1",
        user_agent="pytest",
        response_time_ms=42,
        tags=tags or [],
        user_id=user.id if user else None,
        detail=None,
        request_body=None,
    )
    # ApiAccessLog.user is typed non-optional even though user_id is
    # nullable (a genuinely unauthenticated request has no user) - the model
    # itself is inconsistent here, not this test.
    log.user = user  # type: ignore[assignment]
    return log
