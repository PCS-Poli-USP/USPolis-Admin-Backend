from datetime import timedelta

from sqlmodel import Session, select

from server.models.database.api_access_log_db_model import ApiAccessLog
from server.models.database.api_incident_report_db_model import ApiIncidentReport
from server.services.cron.daily_tasks import purge_old_access_logs
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.enums.api_security_level_enum import APISecurityLevel
from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)
from server.utils.must_be_int import must_be_int


def make_access_log(*, timestamp, session: Session) -> ApiAccessLog:  # type: ignore[no-untyped-def]
    log = ApiAccessLog(
        security_level=APISecurityLevel.PUBLIC,
        endpoint="/test",
        method="GET",
        status_code=500,
        timestamp=timestamp,
        tags=[],
    )
    session.add(log)
    session.flush()
    return log


def test_purge_old_access_logs_deletes_only_rows_older_than_retention(
    session: Session,
) -> None:
    now = BrazilDatetime.now_utc()
    old_log = make_access_log(timestamp=now - timedelta(days=40), session=session)
    recent_log = make_access_log(timestamp=now - timedelta(days=5), session=session)
    session.commit()

    purge_old_access_logs(session)
    session.commit()

    remaining_ids = set(session.exec(select(ApiAccessLog.id)).all())
    assert old_log.id not in remaining_ids
    assert recent_log.id in remaining_ids


def test_purge_old_access_logs_keeps_rows_referenced_by_incident_report(
    session: Session,
) -> None:
    now = BrazilDatetime.now_utc()
    old_log = make_access_log(timestamp=now - timedelta(days=40), session=session)
    session.commit()

    incident = ApiIncidentReport(
        level=IncidentReportLevel.HIGH,
        status=IncidentReportStatus.OPEN,
        description="test incident",
        access_log_id=must_be_int(old_log.id),
    )
    session.add(incident)
    session.commit()

    purge_old_access_logs(session)
    session.commit()

    remaining_ids = set(session.exec(select(ApiAccessLog.id)).all())
    assert old_log.id in remaining_ids
