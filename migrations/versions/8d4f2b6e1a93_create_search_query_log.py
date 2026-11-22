"""create search query log

Revision ID: 8d4f2b6e1a93
Revises: 3b9d7e5a1c24
Create Date: 2026-11-21 10:00:00.000000

Anonymous log of the public searches people settle on, aggregated per day,
normalized query and type filter (searches, searches without results, latest
result count), to find what they look for and do not find. No user, IP or
session data is stored. The unique (day, query, types) key is what the
recording upsert relies on, and it also serves the per-day range scans.

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8d4f2b6e1a93"
down_revision: str | None = "3b9d7e5a1c24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "searchquerylog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column(
            "query", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column(
            "types",
            postgresql.ARRAY(sa.String()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("searches", sa.Integer(), nullable=False),
        sa.Column("empty_searches", sa.Integer(), nullable=False),
        sa.Column("last_result_count", sa.Integer(), nullable=False),
        sa.Column("last_searched_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "day", "query", "types", name="uq_searchquerylog_day_query_types"
        ),
    )


def downgrade() -> None:
    op.drop_table("searchquerylog")
