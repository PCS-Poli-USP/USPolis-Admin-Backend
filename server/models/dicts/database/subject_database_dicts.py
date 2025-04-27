from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.forum_db_model import ForumPost
from server.utils.enums.subject_type import SubjectType


class SubjectModelDict(BaseModelDict):
    """
    Class to hold the model dictionary for the database.
    """

    name: str
    code: str
    professors: list[str]
    type: SubjectType
    class_credit: int
    work_credit: int

    # Relationships
    buildings: list[Building]
    classes: list[Class]
    forum: ForumPost
