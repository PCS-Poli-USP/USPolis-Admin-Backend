"""Who is told about a solicitation by email: whoever can act on it.

A solicitation is approved or denied with RESERVE (see docs/PERMISSIONS.md).
The recipients are:

- with a classroom: whoever holds RESERVE on it (directly or by the building
  cascade);
- with no classroom yet: whoever holds RESERVE on its building or on any
  classroom of it (the same rule as the solicitations inbox);
- plus the members of the matching legacy groups, until groups are retired.

Admins are not recipients for being admins, only through a role or a group.
Only users with `receive_emails` are returned.
"""

from dataclasses import replace

from sqlmodel import Session, col, select

from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_db_model import Classroom
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.solicitation_db_model import Solicitation
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.services.security.role_permission_evaluator import (
    PermissionIndex,
    build_permission_index,
)
from server.utils.enums.actions_enums import ClassroomAction
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int


def solicitation_email_recipients(
    solicitation: Solicitation, session: Session
) -> list[User]:
    classroom = solicitation.reservation.schedule.classroom
    building_id = must_be_int(
        classroom.building_id if classroom else solicitation.building_id
    )
    classroom_ids = (
        [must_be_int(classroom.id)]
        if classroom
        else _classroom_ids_of(building_id, session)
    )

    legacy = classroom.get_users() if classroom else solicitation.building.get_users()
    by_role = [
        user
        for user in _role_candidates(building_id, classroom_ids, session)
        if _can_reserve(_without_admin_bypass(user), building_id, classroom_ids)
    ]

    recipients: dict[int, User] = {}
    for user in [*legacy, *by_role]:
        if user.receive_emails:
            recipients[must_be_int(user.id)] = user
    return list(recipients.values())


def _classroom_ids_of(building_id: int, session: Session) -> list[int]:
    statement = select(Classroom.id).where(Classroom.building_id == building_id)
    return [id for id in session.exec(statement).all() if id is not None]


def _role_candidates(
    building_id: int, classroom_ids: list[int], session: Session
) -> list[User]:
    """Users holding some role with a permission on the building or on one of
    the classrooms (which actions is decided afterwards, by the index)."""
    on_building = (
        select(UserRole.user_id)
        .join(BuildingPermission, col(BuildingPermission.role_id) == UserRole.role_id)
        .where(BuildingPermission.building_id == building_id)
    )
    on_classrooms = (
        select(UserRole.user_id)
        .join(ClassroomPermission, col(ClassroomPermission.role_id) == UserRole.role_id)
        .where(col(ClassroomPermission.classroom_id).in_(classroom_ids))
    )
    user_ids = set(session.exec(on_building).all()) | set(
        session.exec(on_classrooms).all()
    )
    if not user_ids:
        return []
    return list(session.exec(select(User).where(col(User.id).in_(user_ids))).all())


def _without_admin_bypass(user: User) -> PermissionIndex:
    # An admin passes every check; here only what their roles grant counts.
    return replace(build_permission_index(user), is_admin=False)


def _can_reserve(
    index: PermissionIndex, building_id: int, classroom_ids: list[int]
) -> bool:
    if index.has_permission(
        resource=Resource.BUILDING,
        action=ClassroomAction.RESERVE,
        resource_id=building_id,
    ):
        return True
    return any(
        index.has_permission(
            resource=Resource.CLASSROOM,
            action=ClassroomAction.RESERVE,
            resource_id=classroom_id,
        )
        for classroom_id in classroom_ids
    )
