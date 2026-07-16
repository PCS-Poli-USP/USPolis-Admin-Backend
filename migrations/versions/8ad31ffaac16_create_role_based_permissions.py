"""Create role based permissions

Revision ID: 8ad31ffaac16
Revises: c74d94f2efe9
Create Date: 2026-05-15 20:35:08.713046

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8ad31ffaac16"
down_revision: str | None = "c74d94f2efe9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Resource enum creation
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "resources",
            postgresql.ARRAY(sa.Enum("CLASSROOM", "COURSE", name="resource_enum")),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "coursepermission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column(
            "action",
            sa.Enum("CREATE", "READ", "UPDATE", "DELETE", name="courseaction"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["course.id"],
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "action",
            "course_id",
            "user_id",
            "role_id",
            name="unique_action_per_course_permission",
        ),
    )
    op.create_index(
        "unique_action_per_course_permission_role",
        "coursepermission",
        ["action", "course_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )
    op.create_index(
        "unique_action_per_course_permission_user",
        "coursepermission",
        ["action", "course_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )

    op.create_table(
        "userrole",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id", "user_id", "role_id"),
    )

    op.create_table(
        "classroompermission",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.Column("granted_by", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=True),
        sa.Column(
            "action",
            sa.Enum(
                "CREATE",
                "READ",
                "UPDATE",
                "DELETE",
                "ALLOCATE",
                "RESERVE",
                name="classroomaction",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["classroom_id"],
            ["classroom.id"],
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "action",
            "classroom_id",
            "user_id",
            "role_id",
            name="unique_action_per_classroom_permission",
        ),
    )
    op.create_index(
        "unique_action_per_classroom_permission_role",
        "classroompermission",
        ["action", "classroom_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )
    op.create_index(
        "unique_action_per_classroom_permission_user",
        "classroompermission",
        ["action", "classroom_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    # Created with raw SQL (IF NOT EXISTS) instead of op.create_index: the
    # curriculum branch (bf8387c71371_add_course_options_table.py) independently
    # creates these same two indexes, so a straight create would collide once
    # both branches are merged into one history.
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_userabsence_schedule_id '
        'ON userabsence (schedule_id)'
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS ix_userabsence_user_schedule_id '
        'ON userabsence (user_schedule_id)'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP INDEX IF EXISTS ix_userabsence_user_schedule_id")
    op.execute("DROP INDEX IF EXISTS ix_userabsence_schedule_id")
    op.drop_index(
        "unique_action_per_classroom_permission_user",
        table_name="classroompermission",
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.drop_index(
        "unique_action_per_classroom_permission_role",
        table_name="classroompermission",
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )
    op.drop_table("classroompermission")
    op.drop_table("userrole")
    op.drop_index(
        "unique_action_per_course_permission_user",
        table_name="coursepermission",
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.drop_index(
        "unique_action_per_course_permission_role",
        table_name="coursepermission",
        postgresql_where=sa.text("role_id IS NOT NULL"),
    )
    op.drop_table("coursepermission")
    op.drop_table("role")

    ## Drop database enums
    op.execute("DROP TYPE resource_enum")
    op.execute("DROP TYPE courseaction")
    op.execute("DROP TYPE classroomaction")
