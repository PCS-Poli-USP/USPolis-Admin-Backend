from fastapi import UploadFile
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.utils.enums.bug_enums import BugPriority, BugStatus, BugType


class BugReportRegisterDict(BaseRequestDict):
    priority: BugPriority
    type: BugType
    status: BugStatus
    description: str
    evidences: list[UploadFile]
