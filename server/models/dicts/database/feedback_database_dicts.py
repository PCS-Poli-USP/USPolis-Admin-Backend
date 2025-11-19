from datetime import datetime
from server.models.database.user_db_model import User
from server.models.dicts.database.base_database_dicts import BaseModelDict


class FeedbackModelDict(BaseModelDict, total=False):
    user_id: int
    title: str
    message: str
    created_at: datetime

    user: User
