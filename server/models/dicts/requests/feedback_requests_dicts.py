from server.models.dicts.requests.base_requests_dicts import BaseRequestDict


class FeedbackRegisterDict(BaseRequestDict):
    title: str
    message: str
