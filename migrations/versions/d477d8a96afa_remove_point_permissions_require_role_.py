"""Remove point permissions, require role on permissions

Revision ID: d477d8a96afa
Revises: 6c1f6ef0b2a4
Create Date: 2026-07-15 19:44:11.805305

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d477d8a96afa"
down_revision: str | None = "6c1f6ef0b2a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

RESOURCE_COLUMNS = {
    "buildingpermission": "building_id",
    "classroompermission": "classroom_id",
    "coursepermission": "course_id",
}
TABLES_WITH_CHECK_CONSTRAINT = ("classroompermission", "coursepermission")


def upgrade() -> None:
    # Point permissions (role_id IS NULL) are no longer supported: a permission
    # must always belong to a role, so any orphaned point permission is dropped.
    for table in RESOURCE_COLUMNS:
        op.execute(f"DELETE FROM {table} WHERE role_id IS NULL")

    for table, resource_column in RESOURCE_COLUMNS.items():
        prefix = resource_column[:-3]

        op.drop_index(
            f"unique_permission_per_{prefix}_user",
            table_name=table,
            postgresql_where=sa.text("user_id IS NOT NULL"),
        )
        op.drop_index(
            f"unique_permission_per_{prefix}_role",
            table_name=table,
            postgresql_where=sa.text("role_id IS NOT NULL"),
        )
        op.drop_constraint(
            f"unique_permission_per_{prefix}_target", table, type_="unique"
        )

        if table in TABLES_WITH_CHECK_CONSTRAINT:
            op.drop_constraint("permission_check_user_or_role", table, type_="check")

        op.drop_constraint(f"{table}_user_id_fkey", table, type_="foreignkey")
        op.drop_column(table, "user_id")

        op.alter_column(table, "role_id", existing_type=sa.Integer(), nullable=False)

        op.create_unique_constraint(
            f"unique_permission_per_{prefix}_role",
            table,
            [resource_column, "role_id"],
        )


def downgrade() -> None:
    for table, resource_column in RESOURCE_COLUMNS.items():
        prefix = resource_column[:-3]

        op.drop_constraint(
            f"unique_permission_per_{prefix}_role", table, type_="unique"
        )

        op.alter_column(table, "role_id", existing_type=sa.Integer(), nullable=True)

        op.add_column(table, sa.Column("user_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            f"{table}_user_id_fkey", table, "user", ["user_id"], ["id"]
        )

        if table in TABLES_WITH_CHECK_CONSTRAINT:
            op.create_check_constraint(
                "permission_check_user_or_role",
                table,
                "user_id IS NOT NULL OR role_id IS NOT NULL",
            )

        op.create_unique_constraint(
            f"unique_permission_per_{prefix}_target",
            table,
            [resource_column, "user_id", "role_id"],
        )
        op.create_index(
            f"unique_permission_per_{prefix}_user",
            table,
            [resource_column, "user_id"],
            unique=True,
            postgresql_where=sa.text("user_id IS NOT NULL"),
        )
        op.create_index(
            f"unique_permission_per_{prefix}_role",
            table,
            [resource_column, "role_id"],
            unique=True,
            postgresql_where=sa.text("role_id IS NOT NULL"),
        )
