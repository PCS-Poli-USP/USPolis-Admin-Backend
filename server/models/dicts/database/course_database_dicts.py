from datetime import datetime

from server.models.database.curriculum_db_model import Curriculum
from server.models.dicts.base.course_base_dict import CourseBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class CourseModelDict(BaseModelDict, CourseBaseDict, total=False):
    """Class to hold the model dictionary for the database."""

    created_at: datetime
    created_by_id: int
    updated_at: datetime
    updated_by_id: int

    # Relationships
    curriculums: list[Curriculum]
