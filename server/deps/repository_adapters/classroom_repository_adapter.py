from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.repositories.classroom_repository import ClassroomRepository
from server.services.security.buildings_permission_checker import (
    building_permission_checker,
)


class ClassroomRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ):
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids

    def get_all(self) -> list[Classroom]:
        return ClassroomRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_id(self, id: int) -> Classroom:
        return ClassroomRepository.get_by_id_on_buildings(
            building_ids=self.owned_building_ids, id=id, session=self.session
        )

    def create(
        self,
        classroom: ClassroomRegister,
    ) -> Classroom:
        building_permission_checker(self.user, classroom.building_id)
        new_classroom = ClassroomRepository.create(
            classroom=classroom,
            creator=self.user,
            session=self.session,
        )
        self.session.commit()
        self.session.refresh(new_classroom)
        return new_classroom

    def update(
        self,
        classroom_id: int,
        classroom_in: ClassroomRegister,
    ) -> Classroom:
        building_permission_checker(self.user, classroom_in.building_id)
        classroom = ClassroomRepository.update_on_buildings(
            id=classroom_id,
            building_ids=self.owned_building_ids,
            classroom_in=classroom_in,
            session=self.session,
        )
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def delete(self, id: int) -> None:
        ClassroomRepository.delete_on_buildings(
            id=id, building_ids=self.owned_building_ids, session=self.session
        )
        self.session.commit()


ClassroomRepositoryDep = Annotated[ClassroomRepositoryAdapter, Depends()]
