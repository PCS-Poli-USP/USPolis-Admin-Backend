from typing import Annotated

from fastapi import Depends, HTTPException, status

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.building_db_model import Building
from server.models.database.classroom_db_model import Classroom
from server.models.http.requests.classroom_request_models import (
    ClassroomRegister,
    ClassroomUpdate,
)
from server.repositories.classroom_repository import ClassroomRepository
from server.repositories.group_repository import GroupRepository
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.classrooms_permission_checker import (
    ClassroomPermissionChecker,
)
from server.services.security.group_permission_checker import GroupPermissionChecker
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
        self.group_checker = GroupPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Classroom]:
        """Get all classrooms on buildings that the user has access to."""
        if self.user.is_admin:
            return ClassroomRepository.get_all(session=self.session)

        ids = self.user.classrooms_ids_set()
        return ClassroomRepository.get_by_ids(ids=list(ids), session=self.session)

    def get_all_on_building(self, building_id: int) -> list[Classroom]:
        """Get all classrooms on a building that the user has access to."""
        self.building_checker.check_permission(building_id)
        return ClassroomRepository.get_all_on_buildings(
            building_ids=[building_id], session=self.session
        )

    def get_all_on_my_buildings(self) -> list[Classroom]:
        """Get all classrooms on buildings that the user has access to."""
        return ClassroomRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
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

    def __update_groups_classrooms(
        self, classroom: Classroom, input: ClassroomUpdate | ClassroomRegister
    ) -> None:
        if input.group_ids:
            groups = GroupRepository.get_by_ids(
                ids=input.group_ids, session=self.session
            )
            self.group_checker.check_permission(groups)
            groups = [group for group in groups if not group.main]
            for group in groups:
                if group.building_id != input.building_id:
                    raise ClassroomInsertionOnInvalidGroup(
                        group=group.name, classroom=input.name
                    )
                group.classrooms.append(classroom)
                self.session.add(group)

    def create(
        self,
        input: ClassroomRegister,
    ) -> Classroom:
        self.building_checker.check_permission(input.building_id)
        new_classroom = ClassroomRepository.create(
            input=input,
            creator=self.user,
            session=self.session,
        )
        self.__update_groups_classrooms(
            classroom=new_classroom,
            input=input,
        )
        self.session.commit()
        self.session.refresh(new_classroom)
        return new_classroom

    def update(
        self,
        classroom_id: int,
        input: ClassroomUpdate,
    ) -> Classroom:
        self.classroom_checker.check_permission(classroom_id)
        classroom = ClassroomRepository.update(
            id=classroom_id,
            input=input,
            session=self.session,
        )
        self.__update_groups_classrooms(
            classroom=classroom,
            input=input,
        )
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def delete(self, id: int) -> None:
        classroom = ClassroomRepository.get_by_id(id=id, session=self.session)
        self.classroom_checker.check_permission(must_be_int(classroom.id))
        groups = classroom.groups
        for group in groups:
            if len(group.classrooms) == 1:
                raise DeleteLastClassroomOnGroups(classroom=classroom.name)
        self.session.delete(classroom)
        self.session.commit()


class ClassroomInsertionOnInvalidGroup(HTTPException):
    def __init__(self, group: str, classroom: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sala {classroom} não pode ser inserida no grupo {group}",
        )


class DeleteLastClassroomOnGroups(HTTPException):
    def __init__(self, classroom: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A sala {classroom} não pode ser excluída, pois um ou mais grupos irão ficar sem sala",
        )


ClassroomRepositoryDep = Annotated[ClassroomRepositoryAdapter, Depends()]
