from server.models.dicts.base.subject_base_dict import SubjectBaseDict
from server.models.database.building_db_model import Building
from server.models.database.class_db_model import Class
from server.models.database.forum_db_model import ForumPost
from server.models.dicts.database.base_database_dicts import BaseModelDict


class SubjectModelDict(BaseModelDict, SubjectBaseDict, total=False):
    """
    Class to hold the model dictionary for the database.
    """

    # Relationships
    buildings: list[Building]
    classes: list[Class]
    forum: ForumPost | None
