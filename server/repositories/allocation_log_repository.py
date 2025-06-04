from sqlmodel import Session, desc, select
from server.models.database.allocation_log_db_model import AllocationLog
from server.models.database.schedule_db_model import Schedule
from server.models.http.requests.allocation_log_request_models import AllocationLogInput
from server.utils.must_be_int import must_be_int


class AllocationLogRepository:
    @staticmethod
    def create(
        input: AllocationLogInput, schedule: Schedule, session: Session
    ) -> AllocationLog:
        allocation_log = AllocationLog(
            schedule=schedule,
            schedule_id=must_be_int(schedule.id),
            modified_by=input.modified_by,
            modified_at=input.modified_at,
            action=input.action,
            old_classroom=input.old_classroom,
            old_building=input.old_building,
            new_classroom=input.new_classroom,
            new_building=input.new_building,
        )
        session.add(allocation_log)
        return allocation_log

    @staticmethod
    def get_by_schedule_id(schedule_id: int, session: Session) -> list[AllocationLog]:
        statement = (
            select(AllocationLog)
            .where(AllocationLog.schedule_id == schedule_id)
            .order_by(desc(AllocationLog.modified_at))
        )
        logs = session.exec(statement).all()
        return list(logs)
