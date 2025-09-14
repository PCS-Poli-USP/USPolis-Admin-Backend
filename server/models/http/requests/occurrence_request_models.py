from datetime import date, time
from typing import Self

from pydantic import BaseModel, model_validator


class OccurrenceBase(BaseModel):
    schedule_id: int | None = None
    classroom_id: int | None = None
    start_time: time
    end_time: time
    label: str | None = None


class OccurrenceRegister(OccurrenceBase):
    date: date


class OccurrenceUpdate(OccurrenceBase):
    date: date


class OccurenceManyRegister(OccurrenceBase):
    dates: list[date]
    labels: list[str] | None = None
    times: list[tuple[time, time]] | None = None

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if self.labels and len(self.labels) != len(self.dates):
            raise ValueError("The number of labels must match the number of dates.")
        if self.times:
            if len(self.times) != len(self.dates):
                raise ValueError("The number of times must match the number of dates.")
            for time_pair in self.times:
                if len(time_pair) != 2:
                    raise ValueError(
                        "Each time entry must contain a start and end time."
                    )
        return self
