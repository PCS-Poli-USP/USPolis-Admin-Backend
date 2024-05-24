from datetime import datetime

from pydantic import BaseModel

from server.models.database.user_db_model import User
from server.models.http.responses.building_response_models import BuildingResponse


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    name: str
    created_by: str | None = None
    buildings: list[BuildingResponse] | None = None
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        if user.id is None:
            raise ValueError(
                "User ID is None, try refreshing the session if it is newly created"
            )
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            name=user.name,
            created_by=user.created_by.name if user.created_by else None,
            buildings=[
                BuildingResponse.from_building(building) for building in user.buildings
            ]
            if user.buildings
            else None,
            updated_at=user.updated_at,
        )

    @classmethod
    def from_user_list(cls, users: list[User]) -> list["UserResponse"]:
        return [cls.from_user(user) for user in users]
