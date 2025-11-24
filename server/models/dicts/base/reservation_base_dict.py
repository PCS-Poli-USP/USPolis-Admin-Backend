from server.models.dicts.base.base_dict import BaseDict
from server.utils.enums.reservation_type import ReservationType


class ReservationBaseDict(BaseDict, total=False):
    """Base dict for reservation dictionaries (requests and database)"""

    title: str
    type: ReservationType
    reason: str | None
