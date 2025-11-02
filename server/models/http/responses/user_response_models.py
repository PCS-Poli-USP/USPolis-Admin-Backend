from datetime import datetime

from pydantic import BaseModel

from server.models.database.group_db_model import Group
from server.models.database.user_db_model import User
from server.models.http.responses.building_response_models import BuildingResponse
from server.models.http.responses.solicitation_response_models import (
    SolicitationResponse,
)
from server.utils.must_be_int import must_be_int


class UserInfo(BaseModel):
    name: str
    given_name: str
    family_name: str
    picture: str
    email: str
    email_verified: bool


class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    receive_emails: bool
    name: str
    updated_at: datetime
    last_visited: datetime
    user_info: UserInfo | None = None
    created_by: str | None = None
    buildings: list[BuildingResponse] | None = None
    solicitations: list[SolicitationResponse]
    groups: list["UserGroupResponse"]

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=must_be_int(user.id),
            email=user.email,
            is_admin=user.is_admin,
            receive_emails=user.receive_emails,
            name=user.name,
            created_by=user.created_by.name if user.created_by else None,
            buildings=[
                BuildingResponse.from_building(building) for building in user.buildings
            ]
            if user.buildings
            else None,
            solicitations=SolicitationResponse.from_solicitation_list(
                user.solicitations
            ),
            updated_at=user.updated_at,
            last_visited=user.last_visited,
            groups=UserGroupResponse.from_group_list(user.groups),
        )

    @classmethod
    def from_user_list(cls, users: list[User]) -> list["UserResponse"]:
        return [cls.from_user(user) for user in users]


class UserGroupResponse(BaseModel):
    id: int
    name: str
    building_id: int
    building: str
    main: bool
    classroom_strs: list[str]
    classroom_ids: list[int]

    @classmethod
    def from_group(cls, group: Group) -> "UserGroupResponse":
        classrooms = group.classrooms
        main = group.building.main_group_id == group.id
        if main:
            classrooms = group.building.classrooms if group.building.classrooms else []
            classrooms.sort(key=lambda c: c.name)

        return cls(
            id=must_be_int(group.id),
            name=group.name,
            building_id=must_be_int(group.building_id),
            building=group.building.name,
            main=main,
            classroom_strs=[
                f"{classroom.name} ({classroom.building.name})"
                for classroom in classrooms
            ],
            classroom_ids=[must_be_int(classroom.id) for classroom in classrooms],
        )

    @classmethod
    def from_group_list(cls, groups: list[Group]) -> list["UserGroupResponse"]:
        return [cls.from_group(group) for group in groups]
