"""drop api key allowed_origins (browser keys)

Revision ID: d4b7e2a91c50
Revises: 2c1f0a7d9e34
Create Date: 2026-10-29 12:00:00.000000

Browser keys are gone: a key in a partner's front-end code is public, so every
key is a server key and any request with an `Origin` header is rejected.

Before dropping the column, every browser key that isn't revoked yet is
revoked (`revoked_by_id` NULL = done by the system), and its pending delivery
link, if any, is invalidated and wiped, same as invalidating it by hand.
The partner has to ask for a new (server) key.

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d4b7e2a91c50"
down_revision: str | None = "2c1f0a7d9e34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Timestamps are stored as naive Brazil local time (BrazilDatetime.now_utc).
NOW = "timezone('America/Sao_Paulo', now())"
BROWSER_KEYS = "SELECT id FROM apikey WHERE cardinality(allowed_origins) > 0"


def upgrade() -> None:
    op.execute(
        "UPDATE apikeydeliverylink "
        f"SET ciphertext = NULL, nonce = NULL, salt = NULL, invalidated_at = {NOW} "
        "WHERE consumed_at IS NULL AND invalidated_at IS NULL "
        f"AND api_key_id IN ({BROWSER_KEYS})"
    )
    op.execute(
        "UPDATE apikey "
        f"SET revoked_at = {NOW}, updated_at = {NOW}, "
        "revoked_reason = 'Chaves de navegador foram descontinuadas' "
        "WHERE revoked_at IS NULL AND cardinality(allowed_origins) > 0"
    )
    op.drop_column("apikey", "allowed_origins")


def downgrade() -> None:
    # The revocations above are final and are not undone.
    op.add_column(
        "apikey",
        sa.Column(
            "allowed_origins",
            postgresql.ARRAY(sa.String()),
            server_default="{}",
            nullable=False,
        ),
    )
