from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import ClassroomRegister
from server.repositories.classroom_repository import ClassroomRepository
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.utils.must_be_int import must_be_int


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
        self.building_checker = BuildingPermissionChecker(user=user, session=session)
        self.classroom_checker = ClassroomPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Classroom]:
        """Get all classrooms on buildings that the user has access to."""
        ids = self.user.classrooms_ids_set()
        return ClassroomRepository.get_by_ids(ids=list(ids), session=self.session)

    def get_all_on_building(self, building_id: int) -> list[Classroom]:
        """Get all classrooms on a building that the user has access to."""
        self.building_checker.check_permission(building_id)
        return ClassroomRepository.get_all_on_buildings(
            building_ids=[building_id], session=self.session
        )

    def get_by_id(self, id: int) -> Classroom:
        self.classroom_checker.check_permission(object=id)
        classroom = ClassroomRepository.get_by_id(id=id, session=self.session)
        return classroom

    def get_by_name_and_building(self, name: str, building: Building) -> Classroom:
        classroom = ClassroomRepository.get_by_name_and_building(
            name, building, self.session
        )
        self.classroom_checker.check_permission(classroom)
        return classroom

    def create(
        self,
        classroom: ClassroomRegister,
    ) -> Classroom:
        self.building_checker.check_permission(classroom.building_id)
        new_classroom = ClassroomRepository.create(
            input=classroom,
            creator=self.user,
            session=self.session,
        )
        if not self.user.is_admin:
            for group in self.user.groups:
                group.classrooms.append(new_classroom)
                self.session.add(group)

        self.session.commit()
        self.session.refresh(new_classroom)
        return new_classroom

    def update(
        self,
        classroom_id: int,
        classroom_in: ClassroomRegister,
    ) -> Classroom:
        self.classroom_checker.check_permission(classroom_id)
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
        classroom = ClassroomRepository.get_by_id(id=id, session=self.session)
        self.classroom_checker.check_permission(must_be_int(classroom.id))
        ClassroomRepository.delete_on_buildings(
            id=id,
            building_ids=self.owned_building_ids,
            user=self.user,
            session=self.session,
        )
        self.session.commit()


ClassroomRepositoryDep = Annotated[ClassroomRepositoryAdapter, Depends()]
