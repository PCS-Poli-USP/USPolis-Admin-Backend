from datetime import datetime
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.database.reservation_db_model import Reservation
from server.models.database.user_db_model import User
from server.models.dicts.base.solicitation_base_dict import SolicitationBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class SolicitationModelDict(SolicitationBaseDict, BaseModelDict, total=False):
    """TypedDict for Solicitation database model.\n
    This TypedDict is used to define the structure of the Solicitation data.\n
    """

    closed_by: str | None
    deleted_by: str | None
    created_at: datetime
    updated_at: datetime

    solicited_classroom_id: int | None
    reservation_id: int
    user_id: int

    building: Building
    solicited_classroom: Classroom | None
    reservation: Reservation
    user: User
