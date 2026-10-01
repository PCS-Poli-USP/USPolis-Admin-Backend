"""Store permission actions as arrays.

Revision ID: b2f7d1c0a6e3
Revises: 8ad31ffaac16
Create Date: 2026-05-19 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b2f7d1c0a6e3"
down_revision: str | None = "8ad31ffaac16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


COURSE_ACTION_ENUM = sa.Enum(
    "CREATE",
    "READ",
    "UPDATE",
    "DELETE",
    name="courseaction",
    create_type=False,
)
CLASSROOM_ACTION_ENUM = sa.Enum(
    "CREATE",
    "READ",
    "UPDATE",
    "DELETE",
    "ALLOCATE",
    "RESERVE",
    name="classroomaction",
    create_type=False,
)


def upgrade() -> None:
    op.alter_column("classroompermission", "classroom_id", nullable=True)

    op.add_column(
        "coursepermission",
        sa.Column(
            "actions",
            postgresql.ARRAY(COURSE_ACTION_ENUM),
            nullable=True,
        ),
    )
    op.add_column(
        "classroompermission",
        sa.Column(
            "actions",
            postgresql.ARRAY(CLASSROOM_ACTION_ENUM),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE coursepermission SET actions = ARRAY[action] WHERE action IS NOT NULL"
    )
    op.execute(
        "UPDATE classroompermission SET actions = ARRAY[action] WHERE action IS NOT NULL"
    )

    op.drop_index(
        "unique_action_per_course_permission_user",
        table_name="coursepermission",
    )
    op.drop_index(
        "unique_action_per_course_permission_role",
        table_name="coursepermission",
    )
    op.drop_constraint(
        "unique_action_per_course_permission",
        "coursepermission",
        type_="unique",
    )

    op.drop_index(
        "unique_action_per_classroom_permission_user",
        table_name="classroompermission",
    )
    op.drop_index(
        "unique_action_per_classroom_permission_role",
        table_name="classroompermission",
    )
    op.drop_constraint(
        "unique_action_per_classroom_permission",
        "classroompermission",
        type_="unique",
    )

    op.drop_column("coursepermission", "action")
    op.drop_column("classroompermission", "action")

    op.alter_column("coursepermission", "actions", nullable=False)
    op.alter_column("classroompermission", "actions", nullable=False)

    op.create_unique_constraint(
        "unique_permission_per_course_target",
        "coursepermission",
        ["course_id", "user_id", "role_id"],
    )
    op.create_index(
        "unique_permission_per_course_user",
        "coursepermission",
        ["course_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "unique_permission_per_course_role",
        "coursepermission",
        ["course_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )

    op.create_unique_constraint(
        "unique_permission_per_classroom_target",
        "classroompermission",
        ["classroom_id", "user_id", "role_id"],
    )
    op.create_index(
        "unique_permission_per_classroom_user",
        "classroompermission",
        ["classroom_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "unique_permission_per_classroom_role",
        "classroompermission",
        ["classroom_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )


def downgrade() -> None:
    # Set classroom_id as not-null is wrong

    op.drop_index(
        "unique_permission_per_course_user",
        table_name="coursepermission",
    )
    op.drop_index(
        "unique_permission_per_course_role",
        table_name="coursepermission",
    )
    op.drop_constraint(
        "unique_permission_per_course_target",
        "coursepermission",
        type_="unique",
    )

    op.drop_index(
        "unique_permission_per_classroom_user",
        table_name="classroompermission",
    )
    op.drop_index(
        "unique_permission_per_classroom_role",
        table_name="classroompermission",
    )
    op.drop_constraint(
        "unique_permission_per_classroom_target",
        "classroompermission",
        type_="unique",
    )

    op.add_column(
        "coursepermission",
        sa.Column(
            "action",
            COURSE_ACTION_ENUM,
            nullable=True,
        ),
    )
    op.add_column(
        "classroompermission",
        sa.Column(
            "action",
            CLASSROOM_ACTION_ENUM,
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE coursepermission SET action = actions[1] WHERE actions IS NOT NULL"
    )
    op.execute(
        "UPDATE classroompermission SET action = actions[1] WHERE actions IS NOT NULL"
    )

    op.alter_column("coursepermission", "action", nullable=False)
    op.alter_column("classroompermission", "action", nullable=False)

    op.drop_column("coursepermission", "actions")
    op.drop_column("classroompermission", "actions")

    op.create_unique_constraint(
        "unique_action_per_course_permission",
        "coursepermission",
        ["action", "course_id", "user_id", "role_id"],
    )
    op.create_index(
        "unique_action_per_course_permission_user",
        "coursepermission",
        ["action", "course_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "unique_action_per_course_permission_role",
        "coursepermission",
        ["action", "course_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )

    op.create_unique_constraint(
        "unique_action_per_classroom_permission",
        "classroompermission",
        ["action", "classroom_id", "user_id", "role_id"],
    )
    op.create_index(
        "unique_action_per_classroom_permission_user",
        "classroompermission",
        ["action", "classroom_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "unique_action_per_classroom_permission_role",
        "classroompermission",
        ["action", "classroom_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )
