from datetime import datetime
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.models.dicts.base.building_base_dict import BuildingBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class BuildingModelDict(BuildingBaseDict, BaseModelDict, total=False):
    """TypedDict for Building model.\n
    This TypedDict is used to define the structure of the Building data.\n
    """

    created_by_id: int | None
    updated_at: datetime

    # Relationships
    created_by: User
    classrooms: list[Classroom]
    subjects: list[Subject]
    solicitations: list[ClassroomSolicitation]
