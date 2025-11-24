from datetime import time
from typing import Self
from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator


class AllocationEventUpdate(BaseModel):
    desalocate: bool
    all_occurrences: bool
    start_time: time
    end_time: time
    building: str
    classroom: str
    occurrence_id: int | None
    schedule_id: int


class AllocationReuseTarget(BaseModel):
    subject_id: int
    class_ids: list[int]


class AllocationReuseInput(BaseModel):
    building_id: int
    allocation_year: int
    targets: list[AllocationReuseTarget]
    strict: bool = True


class AllocationMapValue(BaseModel):
    schedule_id: int
    classroom_ids: list[int]

    @model_validator(mode="after")
    def validate_body(self) -> Self:
        if len(self.classroom_ids) == 0:
            raise InvalidAllocationMapValue(
                "Cada agenda na reutilização deve possuir pelo menos uma sala!"
            )

        if any([classroom_id <= 0 for classroom_id in self.classroom_ids]):
            raise InvalidAllocationMapValue(
                "Uma ou mais salas tem valores inválidos (ids)"
            )

        if self.schedule_id <= 0:
            raise InvalidAllocationMapValue(
                "Valor inválido (ID) para a agenda na reutilização!"
            )
        return self


class AllocationMapInput(BaseModel):
    allocation_map: list[AllocationMapValue]


class InvalidAllocationMapValue(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
