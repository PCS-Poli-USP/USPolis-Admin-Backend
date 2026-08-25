"""migrate group data into role permission and userrole

Revision ID: 6950bd048a6d
Revises: 761435876363
Create Date: 2026-07-17 22:05:51.515500

"""

from collections.abc import Sequence

from alembic import op
from sqlmodel import Session, col, select

from server.config import CONFIG
from server.models.database.building_db_model import Building
from server.models.database.building_permission_db_model import BuildingPermission
from server.models.database.classroom_permission_db_model import ClassroomPermission
from server.models.database.group_db_model import Group
from server.models.database.role_db_model import Role
from server.models.database.user_db_model import User
from server.models.database.user_role_db_model import UserRole
from server.utils.enums.actions_enums import BuildingAction, ClassroomAction
from server.utils.enums.resources_enums import Resource
from server.utils.must_be_int import must_be_int

# revision identifiers, used by Alembic.
revision: str = "6950bd048a6d"
down_revision: str | None = "761435876363"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DESCRIPTION_MARKER = "Migrado automaticamente"

MIGRATED_BUILDING_ACTIONS = [
    BuildingAction.CREATE,
    BuildingAction.READ,
    BuildingAction.UPDATE,
    BuildingAction.ALLOCATE,
    BuildingAction.RESERVE,
]
MIGRATED_CLASSROOM_ACTIONS = [
    ClassroomAction.CREATE,
    ClassroomAction.READ,
    ClassroomAction.UPDATE,
    ClassroomAction.ALLOCATE,
    ClassroomAction.RESERVE,
]


def _get_migration_admin(session: Session) -> User:
    admin = session.exec(
        select(User).where(User.email == CONFIG.first_superuser_email)
    ).first()
    if admin:
        return admin
    admin = session.exec(select(User).where(col(User.is_admin).is_(True))).first()
    if admin:
        return admin
    raise RuntimeError(
        "Cannot migrate Group data into Role/Permission: no admin user found "
        f"(looked up {CONFIG.first_superuser_email!r} and any is_admin=True user)."
    )


def upgrade() -> None:
    """Migrate group data into role permission and userrole
    The migration upgrade follows this pipeline:
    1. For each building, create a role for the main group and grant it building permissions
    2. For each group in the building, create a role and grant it classroom permissions
    3. For each user in the group, grant them the role of the group

    The building permissions are:
    - CREATE
    - READ
    - UPDATE
    - ALLOCATE
    - RESERVE

    The classroom permissions are:
    - CREATE
    - READ
    - UPDATE
    - ALLOCATE
    - RESERVE
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    buildings = session.exec(select(Building)).all()
    if not buildings:
        return

    admin = _get_migration_admin(session)
    admin_id = must_be_int(admin.id)

    granted_user_role_keys: set[tuple[int, int]] = set()

    def _grant_role_to_group_members(role: Role, group: Group) -> None:
        role_id = must_be_int(role.id)
        for user in group.users:
            user_id = must_be_int(user.id)
            key = (user_id, role_id)
            if key in granted_user_role_keys:
                continue
            granted_user_role_keys.add(key)
            session.add(
                UserRole(user_id=user_id, role_id=role_id, granted_by_id=admin_id)
            )

    for building in buildings:
        main_group = building.main_group
        if main_group is None:
            continue

        main_role = Role(
            name=main_group.name,
            description=(
                f'{DESCRIPTION_MARKER} do grupo principal do prédio "{building.name}"'
            ),
            resources=[Resource.BUILDING],
        )
        session.add(main_role)
        session.flush()
        session.add(
            BuildingPermission(
                role_id=must_be_int(main_role.id),
                building_id=must_be_int(building.id),
                actions=list(MIGRATED_BUILDING_ACTIONS),
                granted_by_id=admin_id,
            )
        )
        _grant_role_to_group_members(main_role, main_group)

        for group in building.groups:
            if group.id == main_group.id:
                continue

            group_role = Role(
                name=group.name,
                description=(
                    f'{DESCRIPTION_MARKER} do grupo "{group.name}" '
                    f'do prédio "{building.name}"'
                ),
                resources=[Resource.CLASSROOM],
            )
            session.add(group_role)
            session.flush()
            for classroom in group.classrooms:
                session.add(
                    ClassroomPermission(
                        role_id=must_be_int(group_role.id),
                        classroom_id=must_be_int(classroom.id),
                        actions=list(MIGRATED_CLASSROOM_ACTIONS),
                        granted_by_id=admin_id,
                    )
                )
            _grant_role_to_group_members(group_role, group)

    session.commit()


def downgrade() -> None:
    """
    Remove all roles and permissions created by the upgrade migration.

    The downgrade follows this pipeline:
    1. Find all roles created by the upgrade migration (by description marker)
    2. For each role, remove all user roles and permissions associated with it
    3. Remove the role itself
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    migrated_role_ids = session.exec(
        select(Role.id).where(col(Role.description).startswith(DESCRIPTION_MARKER))
    ).all()

    for role_id in migrated_role_ids:
        for user_role in session.exec(
            select(UserRole).where(UserRole.role_id == role_id)
        ).all():
            session.delete(user_role)
        for building_permission in session.exec(
            select(BuildingPermission).where(BuildingPermission.role_id == role_id)
        ).all():
            session.delete(building_permission)
        for classroom_permission in session.exec(
            select(ClassroomPermission).where(ClassroomPermission.role_id == role_id)
        ).all():
            session.delete(classroom_permission)

    session.flush()

    for role_id in migrated_role_ids:
        role = session.get(Role, role_id)
        if role:
            session.delete(role)

    session.commit()
