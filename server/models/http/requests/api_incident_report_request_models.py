from typing import Self

from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator

from server.utils.enums.incident_report_enums import (
    IncidentReportLevel,
    IncidentReportStatus,
)


class ApiIncidentReportCreateRequest(BaseModel):
    access_log_id: int
    level: IncidentReportLevel
    description: str

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if len(self.description) == 0:
            raise ApiIncidentReportInvalidInput("Deve-se fornecer uma descrição")
        return self


class ApiIncidentReportStatusUpdateRequest(BaseModel):
    status: IncidentReportStatus


class ApiIncidentReportInvalidInput(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
