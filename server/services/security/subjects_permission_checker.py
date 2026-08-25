from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.repositories.subject_repository import SubjectRepository
from server.services.security.base_permission_checker import PermissionChecker
from server.services.security.buildings_permission_checker import (
    BuildingPermissionChecker,
)
from server.services.security.role_permission_evaluator import PermissionIndex
from server.utils.enums.actions_enums import BuildingAction
from server.utils.must_be_int import must_be_int


class SubjectPermissionChecker(PermissionChecker[Subject]):
    """
    Permission checker for Subject.
    """

    def __init__(
        self, user: User, session: Session, permission_index: PermissionIndex
    ) -> None:
        super().__init__(user=user, session=session)
        self.building_checker = BuildingPermissionChecker(
            user=user, session=session, permission_index=permission_index
        )

    def check_permission(  # type: ignore[override]
        self,
        object: int | Subject | list[int] | list[Subject],
        action: BuildingAction,
    ) -> None:
        """
        Checks the permission of a user for a specific subject.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - subject (int | Subject | list[int] | list[Subject]): The subject ID, Subject object, list of subject IDs, or list of Subject objects for which the permission needs to be checked.
        - action (BuildingAction): The action being performed on the subject(s), checked against the subject's building(s).
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__subject_id_permission_checker(object, action)
        elif isinstance(object, Subject):
            self.__subject_obj_permission_checker(object, action)
        elif isinstance(object, list):
            self.__subject_list_permission_checker(object, action)

    def __subject_id_permission_checker(
        self, subject_id: int, action: BuildingAction
    ) -> None:
        subject = SubjectRepository.get_by_id(id=subject_id, session=self.session)
        self.__subject_obj_permission_checker(subject, action)

    def __subject_obj_permission_checker(
        self, subject: Subject, action: BuildingAction
    ) -> None:
        building_ids = [must_be_int(building.id) for building in subject.buildings]
        if not any(
            self.building_checker.is_allowed(building_id, action)
            for building_id in building_ids
        ):
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar a disciplina {subject.code}"
            )

    def __subject_list_permission_checker(
        self, subjects: list[int] | list[Subject], action: BuildingAction
    ) -> None:
        for subject in subjects:
            if isinstance(subject, Subject):
                self.__subject_obj_permission_checker(subject, action)
            else:
                self.__subject_id_permission_checker(subject, action)


class ForbiddenSubjectAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
