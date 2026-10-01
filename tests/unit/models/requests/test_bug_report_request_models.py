import io
from unittest.mock import Mock

import pytest
from fastapi import UploadFile

from server.models.http.requests.bug_report_request_models import (
    BugReportRegister,
    InvalidUploadFileType,
)
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType


class TestBugReportRegisterAsForm:
    def test_builds_from_form_data_with_no_evidences(self) -> None:
        report = BugReportRegister.as_form(
            priority=BugPriority.HIGH,
            type=BugType.CRASH_ERROR,
            description="Aplicativo trava",
            evidences=[],
        )

        assert report.status == BugStatus.PENDING
        assert report.description == "Aplicativo trava"
        assert report.evidences == []

    def test_accepts_valid_image_evidence(self) -> None:
        evidence = UploadFile(
            file=io.BytesIO(b"fake-image-bytes"),
            filename="screenshot.png",
            headers={"content-type": "image/png"},  # type: ignore[arg-type]
        )

        report = BugReportRegister.as_form(
            priority=BugPriority.LOW,
            type=BugType.UI,
            description="Botão desalinhado",
            evidences=[evidence],
        )

        assert report.evidences == [evidence]

    def test_rejects_an_unsupported_evidence_mime_type(self) -> None:
        evidence = Mock(content_type="application/pdf")

        with pytest.raises(InvalidUploadFileType):
            BugReportRegister.as_form(
                priority=BugPriority.LOW,
                type=BugType.UI,
                description="Botão desalinhado",
                evidences=[evidence],
            )
