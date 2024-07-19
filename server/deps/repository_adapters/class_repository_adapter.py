from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.building_repository import BuildingRepository
from server.repositories.class_repository import ClassRepository
from server.services.security.buildings_permission_checker import (
    building_permission_checker,
)
from server.services.security.class_permission_checker import class_permission_checker


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

    def get_all(self) -> list[Class]:
        return ClassRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids, session=self.session
        )

    def get_by_id(self, id: int) -> Class:
        # building_permission_checker(self.user, id)
        class_ = ClassRepository.get_by_id_on_buildings(
            id=id, building_ids=self.owned_building_ids, session=self.session
        )
        return class_

    def create(self, input: ClassRegister) -> Class:
        building = BuildingRepository.get_by_subject_id(
            subject_id=input.subject_id, session=self.session
        )
        building_permission_checker(user=self.user, building=building)
        new_class = ClassRepository.create(input=input, session=self.session)
        self.session.commit()
        for schedule in new_class.schedules:
            self.session.refresh(schedule)
        return new_class

    def update(self, id: int, input: ClassUpdate) -> Class:
        class_permission_checker(user=self.user, class_=id, session=self.session)
        updated_class = ClassRepository.update(id=id, input=input, session=self.session)
        self.session.commit()
        self.session.refresh(updated_class)
        for schedule in updated_class.schedules:
            self.session.refresh(schedule)
        return updated_class

    def delete(self, id: int) -> None:
        class_permission_checker(user=self.user, class_=id, session=self.session)
        ClassRepository.delete(id=id, session=self.session)
        self.session.commit()

    def delete_many(self, ids: list[int]) -> None:
        class_permission_checker(user=self.user, class_=ids, session=self.session)
        ClassRepository.delete_many(ids=ids, session=self.session)
        self.session.commit()


ClassRepositoryAdapterDep = Annotated[ClassRepositoryAdapter, Depends()]
