from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator

from server.models.http.validators.subject.subject_validator import SubjectValidator
from server.utils.enums.crawler_type_enum import CrawlerType
from server.utils.enums.subject_type import SubjectType


class CrawlSubject(BaseModel):
    subject_codes: list[str]
    calendar_ids: list[int]
    type: CrawlerType


class UpdateCrawlSubject(BaseModel):
    subject_codes: list[str]
    type: CrawlerType


class SubjectRegister(BaseModel):
    building_ids: list[int]
    code: str
    name: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int

    @field_validator("code")
    def validate_code(cls, code: str) -> str:
        if not SubjectValidator.validate_subject_code(code):
            raise SubjectInvalidData("Subject Code must have 7 characters")
        return code

    @field_validator("building_ids")
    def validate_buildings(cls, building_ids: list[int]) -> list[int]:
        if len(building_ids) == 0:
            raise SubjectInvalidData("Buildings must not be empty")
        return building_ids


class SubjectUpdate(SubjectRegister):
    pass


class SubjectInvalidData(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
