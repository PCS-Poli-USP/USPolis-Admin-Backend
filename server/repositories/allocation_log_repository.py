from sqlmodel import Session
from server.models.database.allocation_log_db_model import AllocationLog
from server.models.http.requests.allocation_log_request_models import AllocationLogInput


class AllocationLogRepository:
    @staticmethod
    def create(input: AllocationLogInput, session: Session) -> AllocationLog:
        allocation_log = AllocationLog(
            schedule_id=input.schedule_id,
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
