from datetime import datetime
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.dicts.database.base_database_dicts import BaseModelDict


class GroupModelDict(BaseModelDict, total=False):
    """TypedDict for Group database model.\n
    This TypedDict is used to define the structure of the Group data.\n
    """

    name: str
    updated_at: datetime
    created_at: datetime

    classrooms: list[Classroom]
    users: list[User]
