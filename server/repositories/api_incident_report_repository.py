from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, col, desc, select

from server.models.database.api_incident_report_db_model import ApiIncidentReport
from server.models.page_models import Page, PaginationInput
from server.repositories.api_access_log_repository import ApiAccessLogRepository
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)


class ApiIncidentReportRepository:
    @staticmethod
    def create(
        *,
        access_log_id: int,
        level: IncidentReportLevel,
        description: str,
        session: Session,
    ) -> ApiIncidentReport:
        ApiAccessLogRepository.get_by_id(id=access_log_id, session=session)
        incident = ApiIncidentReport(
            access_log_id=access_log_id,
            level=level,
            description=description,
            status=IncidentReportStatus.OPEN,
        )
        session.add(incident)
        return incident

    @staticmethod
    def get_by_id(*, id: int, session: Session) -> ApiIncidentReport:
        statement = select(ApiIncidentReport).where(col(ApiIncidentReport.id) == id)
        try:
            incident = session.exec(statement).one()
        except NoResultFound:
            raise ApiIncidentReportNotFound(id)
        return incident

    @staticmethod
    def get_all_paginated(
        *,
        pagination: PaginationInput,
        status: IncidentReportStatus | None,
        level: IncidentReportLevel | None,
        session: Session,
    ) -> Page[ApiIncidentReport]:
        statement = select(ApiIncidentReport)
        if status is not None:
            statement = statement.where(col(ApiIncidentReport.status) == status)
        if level is not None:
            statement = statement.where(col(ApiIncidentReport.level) == level)
        statement = statement.order_by(desc(col(ApiIncidentReport.created_at)))
        return Page.paginate(statement, pagination, session)

    @staticmethod
    def update_status(
        *,
        incident: ApiIncidentReport,
        status: IncidentReportStatus,
        session: Session,
    ) -> ApiIncidentReport:
        incident.status = status
        incident.resolved_at = (
            BrazilDatetime.now_utc() if status == IncidentReportStatus.RESOLVED else None
        )
        session.add(incident)
        return incident


class ApiIncidentReportNotFound(HTTPException):
    def __init__(self, id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não foi possível encontrar ApiIncidentReport com id {id}",
        )
