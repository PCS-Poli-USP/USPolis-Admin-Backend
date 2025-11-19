from datetime import datetime
from server.models.database.bug_report_evidence_db_model import BugReportEvidence
from server.models.database.user_db_model import User
from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType


class BugReportModelDict(BaseModelDict, total=False):
    user_id: int
    priority: BugPriority
    type: BugType
    status: BugStatus
    description: str
    created_at: datetime
    resolved_at: datetime | None

    user: User
    evidences: BugReportEvidence
