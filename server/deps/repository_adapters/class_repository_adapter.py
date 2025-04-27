from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.class_repository import ClassRepository
from server.services.security.class_permission_checker import ClassPermissionChecker
from server.services.security.subjects_permission_checker import (
    subject_permission_checker,
)


class ClassRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
    ):
        self.session = session
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.checker = ClassPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Class]:
        return ClassRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_id(self, id: int) -> Class:
        # building_permission_checker(self.user, id)
        class_ = ClassRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(object=class_)
        return class_

    def create(self, input: ClassRegister) -> Class:
        subject_permission_checker(user=self.user, subject=input.subject_id)
        new_class = ClassRepository.create(input=input, session=self.session)
        self.session.commit()
        for schedule in new_class.schedules:
            self.session.refresh(schedule)
        return new_class

    def update(self, id: int, input: ClassUpdate) -> Class:
        self.checker.check_permission(object=id)
        updated_class = ClassRepository.update(
            id=id, input=input, user=self.user, session=self.session
        )
        self.session.commit()
        self.session.refresh(updated_class)
        return updated_class

    def delete(self, id: int) -> None:
        self.checker.check_permission(object=id)
        ClassRepository.delete(id=id, session=self.session)
        self.session.commit()

    def delete_many(self, ids: list[int]) -> None:
        self.checker.check_permission(object=ids)
        ClassRepository.delete_many(ids=ids, session=self.session)
        self.session.commit()


ClassRepositoryDep = Annotated[ClassRepositoryAdapter, Depends()]
