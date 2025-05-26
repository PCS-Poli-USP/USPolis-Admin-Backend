from server.models.dicts.base.subject_base_dict import SubjectBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.utils.enums.crawler_type_enum import CrawlerType


class CrawlSubjectDict(BaseRequestDict):
    subject_codes: list[str]
    calendar_ids: list[int]
    type: CrawlerType


class UpdateCrawlSubjectDict(BaseRequestDict):
    subject_codes: list[str]
    type: CrawlerType


class SubjectRegisterDict(SubjectBaseDict, BaseRequestDict, total=False):
    building_ids: list[int]


class SubjectUpdateDict(SubjectRegisterDict, total=False):
    pass
