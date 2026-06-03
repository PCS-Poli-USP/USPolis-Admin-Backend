from datetime import datetime, date

from pydantic import BaseModel

from server.models.database.user_absence import UserAbsence
from server.utils.must_be_int import must_be_int


class UserAbsenceResponse(BaseModel):
    id: int
    user_schedule_id: int
    schedule_id: int

    absence_date: date
    note: str

    updated_at: datetime
    created_at: datetime

    @classmethod
    def from_absence(cls, absence: UserAbsence) -> "UserAbsenceResponse":
        return UserAbsenceResponse(
            id=must_be_int(absence.id),
            user_schedule_id=absence.user_schedule_id,
            schedule_id=absence.schedule_id,
            absence_date=absence.absence_date,
            note=absence.note,
            updated_at=absence.updated_at,
            created_at=absence.created_at,
        )

    @classmethod
    def from_absences(cls, absences: list[UserAbsence]) -> list["UserAbsenceResponse"]:
        return [UserAbsenceResponse.from_absence(absence) for absence in absences]
