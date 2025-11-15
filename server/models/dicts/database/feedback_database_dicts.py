from server.models.dicts.database.base_database_dicts import BaseModelDict


class FeedbackModelDict(BaseModelDict, total=False):
    user_id: int
    title: str
    