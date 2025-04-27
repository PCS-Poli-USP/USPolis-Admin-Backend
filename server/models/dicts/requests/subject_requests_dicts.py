from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.utils.enums.crawler_type_enum import CrawlerType
from server.utils.enums.subject_type import SubjectType


class CrawlSubjectDict(BaseRequestDict):
    subject_codes: list[str]
    calendar_ids: list[int]
    type: CrawlerType


class UpdateCrawlSubjectDict(BaseRequestDict):
    subject_codes: list[str]
    type: CrawlerType


class SubjectRegisterDict(BaseRequestDict):
    building_ids: list[int]
    code: str
    name: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int


class SubjectUpdateDict(SubjectRegisterDict, total=False):
    pass
