from server.models.database.reservation_db_model import Reservation
from server.models.dicts.base.meeting_base_dict import MeetingBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict


class MeetingModelDict(MeetingBaseDict, BaseModelDict, total=False):
    """TypedDict for Meeting database model.\n
    This TypedDict is used to define the structure of the Meeting data.\n
    """

    reservation_id: int

    reservation: Reservation
