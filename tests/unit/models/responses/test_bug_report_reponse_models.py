from unittest.mock import Mock, patch

from server.models.database.bug_report_evidence_db_model import (
    BugReportEvidenceMetadata,
)
from server.models.http.responses.bug_report_reponse_models import BugReportResponse
from server.utils.enums.bug_enums import BugPriority, BugType
from tests.utils.academic_test_utils import make_user
from tests.utils.bug_report_test_utils import make_bug_report

_PATCH_TARGET = (
    "server.models.http.responses.bug_report_reponse_models."
    "BugReportEvidenceRepository.get_evidences_metadata"
)


class TestBugReportResponse:
    def test_from_report_includes_evidence_metadata(self) -> None:
        user = make_user(name="Ana")
        report = make_bug_report(user=user)
        evidence = BugReportEvidenceMetadata(
            evidence_id=1, report_id=report.id, mime_type="image/png"
        )

        with patch(_PATCH_TARGET, return_value=[evidence]):
            data = BugReportResponse.from_report(report, session=Mock())

        assert data.id == report.id
        assert data.user_name == "Ana"
        assert data.priority == BugPriority.HIGH
        assert data.type == BugType.CRASH_ERROR
        assert data.evidences_ids == [1]
        assert data.mime_types == ["image/png"]

    def test_from_reports(self) -> None:
        user = make_user()
        report1 = make_bug_report(user=user)
        report2 = make_bug_report(user=user)

        with patch(_PATCH_TARGET, return_value=[]):
            data = BugReportResponse.from_reports([report1, report2], session=Mock())

        assert [d.id for d in data] == [report1.id, report2.id]
