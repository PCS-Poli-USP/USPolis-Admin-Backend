from server.models.dicts.base.base_dict import BaseDict


class FeedbackBaseDict(BaseDict):
    title: str
    message: str
