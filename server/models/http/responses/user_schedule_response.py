from datetime import date, datetime

from pydantic import BaseModel

from server.models.database.user_db_model import User
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.http.responses.user_schedule_entry_response import (
    UserScheduleEntryResponse,
)
from server.services.jupiter_crawler.models import (
    JupiterStudentSchedule,
    JupiterStudentSubject,
)
from server.utils.enums.crawler_enums import CrawlerStatus
from server.utils.must_be_int import must_be_int


class UserScheduleResponse(BaseModel):
    id: int | None
    user_id: int
    start_date: date | None = None
    end_date: date | None = None
    entries: list[UserScheduleEntryResponse] = []

    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_user_schedule(
        cls, user: User, user_schedule: UserSchedule | None
    ) -> "UserScheduleResponse":
        if user_schedule is None:
            return UserScheduleResponse(
                id=must_be_int(user.current_schedule_id)
                if user.current_schedule_id is not None
                else None,
                user_id=must_be_int(user.id),
            )
        return UserScheduleResponse(
            id=must_be_int(user_schedule.id),
            user_id=must_be_int(user.id),
            start_date=user_schedule.start_date,
            end_date=user_schedule.end_date,
            entries=UserScheduleEntryResponse.from_user_schedule_entries(
                user_schedule.entries
            ),
            created_at=user_schedule.created_at,
            updated_at=user_schedule.updated_at,
        )


class UserScheduleCrawlResponse(BaseModel):
    status: CrawlerStatus
    updated: bool
    user_schedule: UserScheduleResponse | None
    user_schedule_crawled: JupiterStudentSchedule
    missing_items: list[JupiterStudentSubject] = []
    message: str | None
