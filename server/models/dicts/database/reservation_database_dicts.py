from datetime import datetime
from server.models.database.event_db_model import Event
from server.models.database.exam_db_model import Exam
from server.models.database.meeting_db_model import Meeting
from server.models.database.schedule_db_model import Schedule
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.models.dicts.base.reservation_base_dict import ReservationBaseDict
from server.models.dicts.database.base_database_dicts import BaseModelDict
from server.utils.enums.audiovisual_type_enum import AudiovisualType
from server.utils.enums.reservation_status import ReservationStatus


class ReservationModelDict(ReservationBaseDict, BaseModelDict, total=False):
    """TypedDict for Reservation database model.\n
    This TypedDict is used to define the structure of the Reservation data.\n
    """

    updated_at: datetime
    audiovisual: AudiovisualType
    created_by_id: int
    status: ReservationStatus

    schedule: Schedule
    created_by: User
    solicitation: Solicitation | None
    exam: Exam | None
    event: Event | None
    meeting: Meeting | None
