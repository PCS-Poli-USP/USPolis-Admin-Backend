from fastapi import File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType


VALID_IMG_MIME_TYPE = ["image/jpeg", "image/png"]


class BugReportRegister(BaseModel):
    priority: BugPriority
    type: BugType
    status: BugStatus
    description: str
    evidences: list[UploadFile]

    @classmethod
    def as_form(
        cls,
        priority: BugPriority = Form(...),
        type: BugType = Form(...),
        description: str = Form(...),
        evidences: list[UploadFile] = File(default_factory=list),
    ) -> "BugReportRegister":
        for img in evidences:
            if img.content_type not in VALID_IMG_MIME_TYPE:
                raise InvalidUploadFileType(
                    "O arquivo enviado não é suportado, envie arquivos .png ou .jpeg"
                )

        return BugReportRegister(
            priority=priority,
            type=type,
            status=BugStatus.PENDING,
            description=description,
            evidences=evidences,
        )


class BugReportStatusUpdate(BaseModel):
    status: BugStatus


class InvalidUploadFileType(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
