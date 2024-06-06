import json
from typing import Any, Self

from pydantic import BaseModel, field_validator
from sqlalchemy.types import JSON


class DayTime(BaseModel):
    hours: int
    minutes: int

    @field_validator("hours")
    @classmethod
    def validate_hours(cls, hours: int) -> int:
        if not 0 <= hours < 24:
            raise ValueError("Hours must be between 0 and 23")
        return hours

    @field_validator("minutes")
    @classmethod
    def validate_minutes(cls, minutes: int) -> int:
        if not 0 <= minutes < 60:
            raise ValueError("Minutes must be between 0 and 59")
        return minutes

    @classmethod
    def from_string(cls, time_str: str) -> Self:
        try:
            hours, minutes = map(int, time_str.split(":"))
            return cls(hours=hours, minutes=minutes)
        except ValueError:
            raise ValueError("Invalid time string format, use 'HH:MM'")

    @staticmethod
    def validate_time_str(time_str: str) -> None:
        try:
            hours, minutes = map(int, time_str.split(":"))
            if not (0 <= hours < 24 and 0 <= minutes < 60):
                raise ValueError("Invalid time string format, use 'HH:MM'")
        except ValueError:
            raise ValueError("Invalid time string format, use 'HH:MM'")

    def to_string(self) -> str:
        return f"{self.hours:02d}:{self.minutes:02d}"

    def __lt__(self, other: Self) -> bool:
        return (self.hours, self.minutes) < (other.hours, other.minutes)

    def __le__(self, other: Self) -> bool:
        return (self.hours, self.minutes) <= (other.hours, other.minutes)

    def __gt__(self, other: Self) -> bool:
        return (self.hours, self.minutes) > (other.hours, other.minutes)

    def __ge__(self, other: Self) -> bool:
        return (self.hours, self.minutes) >= (other.hours, other.minutes)


class DayTimeType(JSON):
    def process_bind_param(self, value: DayTime | None, dialect: Any) -> str | None:
        if value is not None:
            return json.dumps(value.model_dump())
        return value

    def process_result_value(self, value: str | None, dialect: Any) -> DayTime | None:
        if value is not None:
            return DayTime.model_validate_json(value)
        return value
