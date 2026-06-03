"""user_schedule_models

Revision ID: 61c169cfae42
Revises: 4ffffa437549
Create Date: 2026-04-19 06:03:46.483963

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "61c169cfae42"
down_revision: str | None = "4ffffa437549"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ## UserSchedule
    op.create_table(
        "userschedule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "end_date >= start_date",
            name="user_schedule_check_end_date_after_start_date",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "user_schedule_user_id_start_date_end_date_idx",
        "userschedule",
        ["user_id", "start_date", "end_date"],
        unique=False,
    )

    # UserAbsence and FK is after userscheduleentry exists

    op.create_table(
        "userabsence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_schedule_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("absence_date", sa.Date(), nullable=False),
        sa.Column("note", sqlmodel.sql.sqltypes.AutoString(), nullable=False),  # pyright: ignore[reportAttributeAccessIssue]
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_schedule_id",
            "schedule_id",
            "absence_date",
            name="user_absence_unique_entry_date",
        ),
    )

    op.create_index(
        op.f("ix_userabsence_absence_date"),
        "userabsence",
        ["absence_date"],
        unique=False,
    )
    op.create_index(
        "user_absence_entry_idx",
        "userabsence",
        ["user_schedule_id", "schedule_id"],
        unique=False,
    )

    # UserScheduleEntry
    op.create_table(
        "userscheduleentry",
        sa.Column("user_schedule_id", sa.Integer(), nullable=False),
        sa.Column("schedule_id", sa.Integer(), nullable=False),
        sa.Column("absence_count", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "absence_count >= 0", name="user_schedule_check_absence_count_non_negative"
        ),
        sa.ForeignKeyConstraint(
            ["schedule_id"],
            ["schedule.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_schedule_id"],
            ["userschedule.id"],
        ),
        sa.PrimaryKeyConstraint("user_schedule_id", "schedule_id"),
    )
    op.create_index(
        op.f("ix_userscheduleentry_schedule_id"),
        "userscheduleentry",
        ["schedule_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_userscheduleentry_user_schedule_id"),
        "userscheduleentry",
        ["user_schedule_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_userabsence_entry",
        "userabsence",
        "userscheduleentry",
        ["user_schedule_id", "schedule_id"],
        ["user_schedule_id", "schedule_id"],
        ondelete="CASCADE",
    )

    op.add_column("user", sa.Column("active", sa.Boolean(), nullable=True))
    op.execute('UPDATE "user" SET active = true')
    op.alter_column("user", "active", nullable=False)

    op.add_column("user", sa.Column("current_schedule_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "user_current_schedule_id_fkey",
        "user",
        "userschedule",
        ["current_schedule_id"],
        ["id"],
    )


def downgrade() -> None:
    # User downgrade
    op.drop_constraint("user_current_schedule_id_fkey", "user", type_="foreignkey")

    op.drop_column("user", "current_schedule_id")
    op.drop_column("user", "active")

    # UserAbscence downgrade
    op.drop_constraint("fk_userabsence_entry", "userabsence", type_="foreignkey")
    op.drop_index("user_absence_entry_idx", table_name="userabsence")
    op.drop_index(op.f("ix_userabsence_absence_date"), table_name="userabsence")
    op.drop_table("userabsence")

    # ScheduleEntry downgrade
    op.drop_index(
        op.f("ix_userscheduleentry_user_schedule_id"), table_name="userscheduleentry"
    )
    op.drop_index(
        op.f("ix_userscheduleentry_schedule_id"), table_name="userscheduleentry"
    )
    op.drop_table("userscheduleentry")

    # UserSchedule downgrade
    op.drop_index(
        "user_schedule_user_id_start_date_end_date_idx", table_name="userschedule"
    )
    op.drop_table("userschedule")
