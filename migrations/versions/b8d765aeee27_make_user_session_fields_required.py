"""Make user_session fields required

Revision ID: b8d765aeee27
Revises: f53cd44becac
Create Date: 2025-12-26 19:09:23.272405

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b8d765aeee27"
down_revision: str | None = "f53cd44becac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remove rows with NULL values in user_agent or ip_address
    op.execute("DELETE FROM usersession WHERE user_agent IS NULL OR ip_address IS NULL")

    op.alter_column(
        "usersession", "user_agent", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "usersession", "ip_address", existing_type=sa.VARCHAR(), nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "usersession", "ip_address", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "usersession", "user_agent", existing_type=sa.VARCHAR(), nullable=True
    )
