from datetime import datetime

from pydantic import BaseModel

from server.models.database.user_db_model import User
from server.models.http.responses.building_response_models import BuildingResponse


class UserResponse(BaseModel):
    id: str
    email: str
    is_admin: bool
    name: str
    created_by: str | None = None
    buildings: list[BuildingResponse] | None = None
    updated_at: datetime

    @classmethod
    async def from_user(cls, user: User) -> "UserResponse":
        await user.fetch_all_links()
        return cls(
            id=str(user.id),
            email=user.email,
            is_admin=user.is_admin,
            name=user.name,
            created_by=user.created_by.name if user.created_by else None,
            buildings=[
                await BuildingResponse.from_building(building) for building in user.buildings
            ]
            if user.buildings
            else None,
            updated_at=user.updated_at,
        )
    
    @classmethod
    async def from_user_list(cls, users: list[User]) -> list["UserResponse"]:
        return [await cls.from_user(user) for user in users]
