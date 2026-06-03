from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from server.models.database.schedule_db_model import Schedule
from server.models.database.user_db_model import User
from server.models.database.user_schedule_db_model import UserSchedule
from server.models.database.user_schedule_entry_db_model import UserScheduleEntry
from server.utils.brazil_datetime import BrazilDatetime
from server.utils.must_be_int import must_be_int


class UserScheduleRepository:
    @staticmethod
    def _check_schedules_are_active(schedules: list[Schedule]) -> None:
        for schedule in schedules:
            if not schedule.is_active():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agenda com id {must_be_int(schedule.id)} não está ativa",
                )

    @staticmethod
    def get_by_id(id: int, session: Session) -> UserSchedule | None:
        return session.get(UserSchedule, id)

    @staticmethod
    def get_active_current_schedule(
        user: User, session: Session
    ) -> tuple[UserSchedule | None, bool]:
        current_schedule = user.current_schedule
        if current_schedule is None:
            return None, False

        today = BrazilDatetime.now_utc().date()
        if current_schedule.end_date < today:
            user.current_schedule = None
            user.current_schedule_id = None
            session.add(user)
            return None, True

        return current_schedule, False

    @staticmethod
    def invalidate_expired_current_schedules(session: Session) -> list[int]:
        today = BrazilDatetime.now_utc().date()
        statement = (
            select(User)
            .join(UserSchedule, col(User.current_schedule_id) == col(UserSchedule.id))
            .where(col(User.current_schedule_id).is_not(None))
            .where(col(UserSchedule.end_date) < today)
        )
        users = session.exec(statement).all()

        invalidated_ids: list[int] = []
        for user in users:
            invalidated_ids.append(must_be_int(user.current_schedule_id))
            user.current_schedule = None
            user.current_schedule_id = None
            session.add(user)

        return invalidated_ids

    @staticmethod
    def update_from_schedules(
        user_schedule: UserSchedule, schedules: list[Schedule], session: Session
    ) -> UserSchedule:
        UserScheduleRepository._check_schedules_are_active(schedules)

        today = BrazilDatetime.now_utc().date()
        start_date = min((schedule.start_date for schedule in schedules), default=today)
        end_date = max((schedule.end_date for schedule in schedules), default=today)

        user_schedule.start_date = start_date
        user_schedule.end_date = end_date

        existing_entries = {
            must_be_int(entry.schedule_id): entry for entry in user_schedule.entries
        }

        desired_entries = []
        seen_schedule_ids = set()
        for schedule in schedules:
            schedule_id = must_be_int(schedule.id)
            if schedule_id in seen_schedule_ids:
                continue

            seen_schedule_ids.add(schedule_id)
            entry = existing_entries.get(schedule_id)
            if entry is None:
                entry = UserScheduleEntry(
                    user_schedule_id=must_be_int(user_schedule.id),
                    schedule_id=schedule_id,
                )
                session.add(entry)

            desired_entries.append(entry)

        user_schedule.entries = desired_entries
        user_schedule.updated_at = BrazilDatetime.now_utc()
        session.add(user_schedule)
        return user_schedule

    @staticmethod
    def create_from_schedules(
        user: User, schedules: list[Schedule], session: Session
    ) -> UserSchedule:
        UserScheduleRepository._check_schedules_are_active(schedules)

        today = BrazilDatetime.now_utc().date()
        start_date = min((schedule.start_date for schedule in schedules), default=today)
        end_date = max((schedule.end_date for schedule in schedules), default=today)

        user_schedule = UserSchedule(
            user=user,
            user_id=must_be_int(user.id),
            start_date=start_date,
            end_date=end_date,
            created_at=BrazilDatetime.now_utc(),
            updated_at=BrazilDatetime.now_utc(),
        )

        session.add(user_schedule)
        session.flush()

        entries = [
            UserScheduleEntry(
                user_schedule_id=must_be_int(user_schedule.id),
                schedule_id=must_be_int(schedule.id),
            )
            for schedule in schedules
        ]
        session.add_all(entries)
        return user_schedule

    @staticmethod
    def delete(user_schedule: UserSchedule, session: Session) -> None:
        # for entry in user_schedule.entries:
        #     session.delete(entry)
        session.delete(user_schedule)
