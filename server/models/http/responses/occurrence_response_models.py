from datetime import time
from datetime import date as datetime_date
from pydantic import BaseModel

from server.models.database.occurrence_db_model import Occurrence
from server.utils.must_be_int import must_be_int


class OccurrenceBase(BaseModel):
    id: int
    start_time: time
    end_time: time
    date: datetime_date
    classroom_id: int | None = None
    classroom: str | None = None
    label: str | None = None


class OccurrenceResponse(OccurrenceBase):
    @classmethod
    def from_occurrence(cls, occurrence: Occurrence) -> "OccurrenceResponse":
        return cls(
            id=must_be_int(occurrence.id),
            start_time=occurrence.start_time,
            end_time=occurrence.end_time,
            date=occurrence.date,
            classroom_id=occurrence.classroom_id,
            classroom=occurrence.classroom.name if occurrence.classroom else None,
            label=occurrence.occurrence_label.label
            if occurrence.occurrence_label
            else None,
        )

    @classmethod
    def from_occurrence_list(
        cls, occurrences: list[Occurrence]
    ) -> list["OccurrenceResponse"]:
        return [
            OccurrenceResponse.from_occurrence(occurrence) for occurrence in occurrences
        ]
