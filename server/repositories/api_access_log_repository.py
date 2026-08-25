from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, desc, func, select

from server.models.database.api_access_log_db_model import ApiAccessLog
from server.models.database.api_incident_report_db_model import ApiIncidentReport
from server.models.page_models import Page, PaginationInput
from server.utils.enums.api_security_level_enum import APISecurityLevel


class ApiAccessLogRepository:
    @staticmethod
    def create(
        *,
        security_level: APISecurityLevel,
        endpoint: str,
        method: str,
        status_code: int,
        ip_address: str | None,
        user_agent: str | None,
        response_time_ms: int | None,
        tags: list[str],
        user_id: int | None,
        detail: str | None,
        request_body: str | None,
        session: Session,
    ) -> ApiAccessLog:
        access_log = ApiAccessLog(
            security_level=security_level,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            response_time_ms=response_time_ms,
            tags=tags,
            user_id=user_id,
            detail=detail[:500] if detail else None,
            request_body=request_body[:2000] if request_body else None,
        )
        session.add(access_log)
        return access_log

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> ApiAccessLog:
        statement = select(ApiAccessLog).where(col(ApiAccessLog.id) == id)
        try:
            access_log = session.exec(statement).one()
        except NoResultFound:
            raise ApiAccessLogNotFound(id)
        return access_log

    @staticmethod
    def get_all_paginated(
        *,
        pagination: PaginationInput,
        status_code: int | None,
        method: str | None,
        security_level: APISecurityLevel | None,
        since: datetime | None,
        until: datetime | None,
        session: Session,
    ) -> Page[ApiAccessLog]:
        statement = select(ApiAccessLog)
        if status_code is not None:
            statement = statement.where(col(ApiAccessLog.status_code) == status_code)
        if method is not None:
            statement = statement.where(col(ApiAccessLog.method) == method.upper())
        if security_level is not None:
            statement = statement.where(
                col(ApiAccessLog.security_level) == security_level
            )
        if since is not None:
            statement = statement.where(col(ApiAccessLog.timestamp) >= since)
        if until is not None:
            statement = statement.where(col(ApiAccessLog.timestamp) <= until)
        statement = statement.order_by(desc(col(ApiAccessLog.timestamp)))
        return Page.paginate(statement, pagination, session)

    @staticmethod
    def get_summary(
        *, since: datetime, session: Session
    ) -> list[tuple[int, int]]:
        """Returns (status_code, count) pairs for rows created since `since`."""
        statement = (
            select(ApiAccessLog.status_code, func.count())
            .where(col(ApiAccessLog.timestamp) >= since)
            .group_by(col(ApiAccessLog.status_code))
            .order_by(col(ApiAccessLog.status_code))
        )
        return list(session.exec(statement).all())

    @staticmethod
    def delete_older_than(*, cutoff: datetime, session: Session) -> int:
        """Used by the retention job. Rows still referenced by an
        ApiIncidentReport are kept regardless of age, so a tracked incident
        never loses its originating log context. Caller commits."""
        statement = select(ApiAccessLog).where(
            col(ApiAccessLog.timestamp) < cutoff,
            col(ApiAccessLog.id).not_in(select(ApiIncidentReport.access_log_id)),
        )
        rows = list(session.exec(statement).all())
        for row in rows:
            session.delete(row)
        return len(rows)


class ApiAccessLogNotFound(HTTPException):
    def __init__(self, id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível encontrar ApiAccessLog com id {id}",
        )
