from datetime import datetime

from server.models.database.building_db_model import Building
from server.models.database.classroom_solicitation_db_model import ClassroomSolicitation
from server.models.database.group_db_model import Group
from server.models.database.occurrence_db_model import Occurrence
from server.models.database.reservation_db_model import Reservation
from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.dicts.base.classroom_base_dict import ClassroomBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class ClassroomModelDict(ClassroomBaseDict, BaseModelDict, total=False):
    """TypedDict for Classroom model.\n
    This TypedDict is used to define the structure of the Classroom data.\n
    """

    building_id: int
    created_by_id: int
    updated_at: datetime

    # Relationships
    created_by: User
    building: Building
    schedules: list[Schedule]
    occurrences: list[Occurrence]
    reservations: list[Reservation]
    solicitations: list[ClassroomSolicitation]
    groups: list[Group]
