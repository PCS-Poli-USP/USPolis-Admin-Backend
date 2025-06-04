from typing import Annotated

from fastapi import Depends

from server.deps.authenticate import UserDep
from server.deps.interval_dep import QueryIntervalDep
from server.deps.owned_building_ids import OwnedBuildingIdsDep
from server.deps.session_dep import SessionDep
from server.models.database.class_db_model import Class
from server.models.http.requests.class_request_models import ClassRegister, ClassUpdate
from server.repositories.class_repository import ClassRepository
from server.services.security.class_permission_checker import ClassPermissionChecker
from server.services.security.schedule_permission_checker import (
    SchedulePermissionChecker,
)
from server.services.security.subjects_permission_checker import (
    SubjectPermissionChecker,
)


class ClassRepositoryAdapter:
    def __init__(
        self,
        owned_building_ids: OwnedBuildingIdsDep,
        session: SessionDep,
        user: UserDep,
        interval: QueryIntervalDep,
    ):
        self.session = session
        self.interval = interval
        self.user = user
        self.owned_building_ids = owned_building_ids
        self.checker = ClassPermissionChecker(user=user, session=session)
        self.schedule_checker = SchedulePermissionChecker(user=user, session=session)
        self.subject_checker = SubjectPermissionChecker(user=user, session=session)

    def get_all(self) -> list[Class]:
        """Get all class on buildings that the user has access to."""
        if self.user.is_admin:
            return ClassRepository.get_all(session=self.session, interval=self.interval)
        classes = self.get_all_on_my_classrooms()
        classes.extend(self.get_all_unallocated())
        return classes

    def get_all_on_my_classrooms(self) -> list[Class]:
        """Get all classes on classrooms that the user has access to."""
        return ClassRepository.get_all_on_classrooms(
            classroom_ids=self.user.classrooms_ids(),
            session=self.session,
            interval=self.interval,
        )

    def get_all_unallocated(self) -> list[Class]:
        """Get all classes that are not allocated in all schedules and are in one of the buildings."""
        return ClassRepository.get_all_unallocated_on_buildings(
            building_ids=self.owned_building_ids,
            session=self.session,
            interval=self.interval,
        )

    def get_all_on_my_buildings(self) -> list[Class]:
        """Get all classes on buildings that the user has access to."""
        return ClassRepository.get_all_on_buildings(
            building_ids=self.owned_building_ids,
            session=self.session,
            interval=self.interval,
        )

    def get_by_id(self, id: int) -> Class:
        class_ = ClassRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(object=class_)
        return class_

    def create(self, input: ClassRegister) -> Class:
        self.subject_checker.check_permission(object=input.subject_id)
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
        class_ = ClassRepository.get_by_id(id=id, session=self.session)
        self.checker.check_permission(object=class_)
        self.schedule_checker.check_permission(object=class_.schedules)
        ClassRepository.delete(id=id, session=self.session)
        self.session.commit()

    def delete_many(self, ids: list[int]) -> None:
        classes = ClassRepository.get_by_ids(
            ids=ids, session=self.session
        )
        self.checker.check_permission(object=classes)

        for class_ in classes:
            self.schedule_checker.check_permission(object=class_.schedules)
            
        ClassRepository.delete_many(ids=ids, session=self.session)
        self.session.commit()


ClassRepositoryDep = Annotated[ClassRepositoryAdapter, Depends()]
