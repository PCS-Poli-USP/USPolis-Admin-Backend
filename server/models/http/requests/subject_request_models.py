from datetime import datetime

from pydantic import BaseModel, field_validator

from server.models.validators.subject.subject_validator import SubjectValidator
from server.utils.enums.subject_type import SubjectType


class SubjectRegister(BaseModel):
    code: str
    name: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int
    activation: datetime
    desactivation: datetime | None = None

    @field_validator("code")
    def validate_code(cls, code: str) -> str:
        if not SubjectValidator.validate_subject_code(code):
            raise ValueError("Subject Code must have 7 characters")
        return code


class SubjectUpdate(SubjectRegister):
    pass
