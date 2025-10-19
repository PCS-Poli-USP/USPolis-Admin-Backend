from server.models.dicts.base.exam_base_dict import ExamBaseDict
from server.models.dicts.requests.base_requests_dicts import BaseRequestDict
from server.models.dicts.requests.reservation_requests_dicts import (
    ReservationRegisterDict,
    ReservationUpdateDict,
)


class EventRegisterDict(
    ReservationRegisterDict, ExamBaseDict, BaseRequestDict, total=False
):
    class_ids: list[int]


class EventUpdateDict(
    ReservationUpdateDict, ExamBaseDict, BaseRequestDict, total=False
):
    class_ids: list[int]
