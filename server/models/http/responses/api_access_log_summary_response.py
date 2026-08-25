from pydantic import BaseModel


class StatusCodeCount(BaseModel):
    status_code: int
    count: int


class ApiAccessLogSummaryResponse(BaseModel):
    since_days: int
    total_errors: int
    by_status_code: list[StatusCodeCount]
