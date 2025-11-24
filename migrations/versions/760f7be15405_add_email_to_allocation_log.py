"""Add email to allocation log

Revision ID: 760f7be15405
Revises: 25815c8def9f
Create Date: 2025-08-15 19:11:21.748625

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "760f7be15405"
down_revision: str | None = "25815c8def9f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "allocationlog",
        sa.Column("user_email", sqlmodel.sql.sqltypes.AutoString(), nullable=True),  # type: ignore
    )
    op.execute(
        """
    UPDATE allocationlog AS al
    SET user_email = u.email
    FROM "user" AS u
    WHERE u.name = al.modified_by
    """
    )
    op.alter_column(
        "allocationlog",
        "user_email",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("allocationlog", "user_email")
