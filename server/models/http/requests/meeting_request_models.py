from server.models.http.requests.reservation_request_models import ReservationRegister


class MeetingBase(ReservationRegister):
    link: str | None = None


class MeetingRegister(MeetingBase):
    pass


class MeetingUpdate(MeetingBase):
    pass
