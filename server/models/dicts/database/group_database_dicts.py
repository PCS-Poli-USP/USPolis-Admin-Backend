from datetime import datetime
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.user_db_model import User
from server.models.dicts.base.group_base_dict import GroupBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class GroupModelDict(GroupBaseDict, BaseModelDict, total=False):
    """TypedDict for Group database model.\n
    This TypedDict is used to define the structure of the Group data.\n
    """

    updated_at: datetime
    created_at: datetime

    building: Building
    classrooms: list[Classroom]
    users: list[User]
