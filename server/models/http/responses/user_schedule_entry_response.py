from pydantic import BaseModel

from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from server.models.http.responses.schedule_response_models import ScheduleResponseBase
from server.models.http.responses.user_absence_response import UserAbsenceResponse


class UserScheduleEntryResponse(BaseModel):
    user_schedule_id: int
    schedule_id: int
    absence_count: int
    schedule_data: ScheduleResponseBase
    absences: list[UserAbsenceResponse] = []

    @classmethod
    def from_user_schedule_entry(
        cls, user_schedule_entry: UserScheduleEntry
    ) -> "UserScheduleEntryResponse":
        return UserScheduleEntryResponse(
            user_schedule_id=user_schedule_entry.user_schedule_id,
            schedule_id=user_schedule_entry.schedule_id,
            absence_count=user_schedule_entry.absence_count,
            schedule_data=ScheduleResponseBase.from_schedule(
                user_schedule_entry.schedule
            ),
            absences=UserAbsenceResponse.from_absences(user_schedule_entry.absences),
        )

    @classmethod
    def from_user_schedule_entries(
        cls, user_schedule_entries: list[UserScheduleEntry]
    ) -> list["UserScheduleEntryResponse"]:
        return [
            UserScheduleEntryResponse.from_user_schedule_entry(entry)
            for entry in user_schedule_entries
        ]
