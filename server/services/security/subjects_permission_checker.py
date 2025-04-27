from fastapi import HTTPException
from sqlmodel import Session

from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.services.security.base_permission_checker import PermissionChecker
from server.utils.must_be_int import must_be_int


class SubjectPermissionChecker(PermissionChecker[Subject]):
    """
    Permission checker for Subject.
    """

    def __init__(self, user: User, session: Session) -> None:
        super().__init__(user=user, session=session)

    def check_permission(
        self,
        object: int | Subject | list[int] | list[Subject],
    ) -> None:
        """
        Checks the permission of a user for a specific subject.

        Parameters:
        - user (User): The user object for which the permission needs to be checked.
        - subject (int | Subject | list[int] | list[Subject]): The subject ID, Subject object, list of subject IDs, or list of Subject objects for which the permission needs to be checked.
        """
        if self.user.is_admin:
            return

        if isinstance(object, int):
            self.__subject_id_permission_checker(object)
        elif isinstance(object, Subject):
            self.__subject_obj_permission_checker(object)
        elif isinstance(object, list):
            self.__subject_list_permission_checker(object)

    def __subject_id_permission_checker(self, subject_id: int) -> None:
        if self.user.buildings is None:
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar a disciplina com ID {subject_id}"
            )
        subjects_ids: list[int] = []
        for building in self.user.buildings:
            if building.subjects is not None:
                subjects_ids += [
                    must_be_int(subject.id) for subject in building.subjects
                ]
        if subject_id not in subjects_ids:
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar a disciplina com ID {subject_id}"
            )

    def __subject_obj_permission_checker(self, subject: Subject) -> None:
        if self.user.buildings is None:
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar a disciplina {subject.code}"
            )
        must_be_int(subject.id)
        building_ids = [building.id for building in subject.buildings]
        user_buildings_ids = self.user.buildings_ids_set()
        if len(set(building_ids).intersection(user_buildings_ids)) == 0:
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar a disciplina {subject.code}"
            )

    def __subject_list_permission_checker(
        self, subjects: list[int] | list[Subject]
    ) -> None:
        subject_ids: list[int] = [
            must_be_int(subject.id) if isinstance(subject, Subject) else subject
            for subject in subjects
        ]

        if self.user.buildings is None:
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar as disciplinas com ID's {subject_ids}"
            )

        user_subjects_ids: list[int] = []
        for building in self.user.buildings:
            if building.subjects is not None:
                user_subjects_ids += [
                    must_be_int(subject.id) for subject in building.subjects
                ]
        if not set(subject_ids).issubset(set(user_subjects_ids)):
            raise ForbiddenSubjectAccess(
                f"Usuário não tem permissão para acessar uma ou mais das disciplinas com ID's {subject_ids}"
            )


class ForbiddenSubjectAccess(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403,
            detail=detail,
        )
