from server.models.database.reservation_db_model import Reservation
from server.models.dicts.base.event_base_dict import EventBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.utils.enums.event_type_enum import EventType


class EventModelDict(EventBaseDict, BaseModelDict, total=False):
    """TypedDict for Event database model.\n
    This TypedDict is used to define the structure of the Event data.\n
    """

    reservation_id: int
    type: EventType

    reservation: Reservation
