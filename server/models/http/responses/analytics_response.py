from pydantic import BaseModel


class APIAnalyticsResponse(BaseModel):
    total_requests: int
    average_response_time_ms: float
    requests_by_status: dict[int, int]
    top_endpoints: list[tuple[str, int]]
