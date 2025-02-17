from fastapi import HTTPException

from server.models.database.subject_db_model import Subject
from server.models.database.user_db_model import User
from server.utils.must_be_int import must_be_int


def subject_permission_checker(
    user: User, subject: int | Subject | list[int] | list[Subject]
) -> None:
    """
    Checks the permission of a user for a specific subject.

    Parameters:
    - user (User): The user object for which the permission needs to be checked.
    - subject (int | Subject | list[int] | list[Subject]): The subject ID, Subject object, list of subject IDs, or list of Subject objects for which the permission needs to be checked.
    """
    if user.is_admin:
        return

    if isinstance(subject, int):
        __subject_id_permission_checker(user, subject)
    elif isinstance(subject, Subject):
        __subject_obj_permission_checker(user, subject)
    elif isinstance(subject, list):
        __subject_list_permission_checker(user, subject)


def __subject_id_permission_checker(user: User, subject_id: int) -> None:
    if user.buildings is None:
        raise ForbiddenSubjectAccess([subject_id])
    subjects_ids: list[int] = []
    for building in user.buildings:
        if building.subjects is not None:
            subjects_ids += [must_be_int(subject.id) for subject in building.subjects]
    if subject_id not in subjects_ids:
        raise ForbiddenSubjectAccess([subject_id])


def __subject_obj_permission_checker(user: User, subject: Subject) -> None:
    if user.buildings is None:
        raise ForbiddenSubjectAccess([subject.id])  # type: ignore

    must_be_int(subject.id)
    building_ids = [building.id for building in subject.buildings]
    user_buildings_ids = [building.id for building in user.buildings]
    if not set(building_ids).issubset(set(user_buildings_ids)):
        raise ForbiddenSubjectAccess([subject.id])  # type: ignore


def __subject_list_permission_checker(
    user: User, subjects: list[int] | list[Subject]
) -> None:
    subject_ids: list[int] = [
        must_be_int(subject.id) if isinstance(subject, Subject) else subject
        for subject in subjects
    ]

    if user.buildings is None:
        raise ForbiddenSubjectAccess(subject_ids)

    user_subjects_ids: list[int] = []
    for building in user.buildings:
        if building.subjects is not None:
            user_subjects_ids += [
                must_be_int(subject.id) for subject in building.subjects
            ]
    if not set(subject_ids).issubset(set(user_subjects_ids)):
        raise ForbiddenSubjectAccess(subject_ids)  # type: ignore


class ForbiddenSubjectAccess(HTTPException):
    def __init__(self, subject_ids: list[int]):
        super().__init__(
            status_code=403,
            detail=f"User do not have access to subjects: {subject_ids}",
        )
