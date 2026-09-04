"""Shared, DB-free helper for building BugReport object graphs in pure unit
tests (no session, nothing persisted).

Constructed directly rather than via a ModelFactory - no factory/dict
scaffolding exists for BugReport yet, and it's only needed by a couple of
response/request-model tests, so a full base-dict/model-dict/base-factory/
model-factory stack would be pure overhead. See TESTS.md's "Test data
protocol" section before adding a new make_* helper here."""

from datetime import datetime

from server.models.database.bug_report_db_model import BugReport
from server.models.database.user_db_model import User
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType

_next_id = iter(range(1, 1_000_000))


def make_bug_report(
    *,
    user: User,
    priority: BugPriority = BugPriority.HIGH,
    type: BugType = BugType.CRASH_ERROR,
    status: BugStatus = BugStatus.PENDING,
    description: str = "Aplicativo trava ao abrir",
) -> BugReport:
    report = BugReport(
        id=next(_next_id),
        user_id=user.id,
        priority=priority,
        type=type,
        status=status,
        description=description,
        created_at=datetime(2025, 1, 1),
        resolved_at=None,
    )
    report.user = user
    return report
