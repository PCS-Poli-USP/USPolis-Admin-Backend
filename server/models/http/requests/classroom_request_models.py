from typing import Self
from fastapi import HTTPException, status
from pydantic import BaseModel, model_validator
from datetime import time, date

from server.utils.enums.audiovisual_type_enum import AudiovisualType


class ClassroomRegister(BaseModel):
    building_id: int
    group_ids: list[int]

    name: str
    capacity: int
    floor: int
    accessibility: bool
    audiovisual: AudiovisualType
    air_conditioning: bool
    observation: str = ""

    @model_validator(mode="after")
    def check_classroom_body(self) -> Self:
        group_ids = self.group_ids

        if len(group_ids) == 0:
            raise ClassroomInvalidRequest(
                message="Uma sala deve ter pelo menos um grupo associado."
            )
        return self


class ClassroomUpdate(ClassroomRegister):
    pass


class ClassroomConflictCheck(BaseModel):
    start_time: time
    end_time: time
    dates: list[date]


class ClassroomInvalidRequest(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
