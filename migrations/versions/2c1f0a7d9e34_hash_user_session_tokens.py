"""hash user session tokens

Revision ID: 2c1f0a7d9e34
Revises: 8feb53242f11
Create Date: 2026-10-17 21:00:00.000000

The `session` cookie used to be the row's primary key, stored in plain text:
a database dump or backup was enough to hijack every live session. New
sessions get a random token whose SHA-256 is all that is stored.

Existing rows are backfilled with sha256(id), so the cookies browsers already
hold keep working and nobody is logged out. Those rows still have
id == cookie until they expire (at most SESSION_MAX_AGE_DAYS = 90 days).

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "2c1f0a7d9e34"
down_revision: str | None = "8feb53242f11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usersession",
        sa.Column("token_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    # Same digest as hash_session_token(): hex SHA-256 of the UTF-8 value.
    op.execute(
        "UPDATE usersession "
        "SET token_hash = encode(sha256(convert_to(id, 'UTF8')), 'hex')"
    )
    op.alter_column("usersession", "token_hash", nullable=False)
    op.create_index(
        op.f("ix_usersession_token_hash"), "usersession", ["token_hash"], unique=True
    )


def downgrade() -> None:
    # Sessions created after the upgrade have random ids unrelated to their
    # cookies: after a downgrade, those users have to log in again.
    op.drop_index(op.f("ix_usersession_token_hash"), table_name="usersession")
    op.drop_column("usersession", "token_hash")
