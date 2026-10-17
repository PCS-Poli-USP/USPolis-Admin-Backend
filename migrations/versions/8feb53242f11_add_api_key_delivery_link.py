"""add api key delivery link

Revision ID: 8feb53242f11
Revises: cb3f76a41931
Create Date: 2026-10-17 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "8feb53242f11"
down_revision: Union[str, None] = "cb3f76a41931"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apikeydeliverylink",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("api_key_id", sa.Integer(), nullable=False),
        sa.Column(
            "link_id", sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False
        ),
        sa.Column("ciphertext", sa.LargeBinary(), nullable=True),
        sa.Column("nonce", sa.LargeBinary(), nullable=True),
        sa.Column("salt", sa.LargeBinary(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "consumed_ip", sqlmodel.sql.sqltypes.AutoString(length=45), nullable=True
        ),
        sa.Column(
            "consumed_user_agent",
            sqlmodel.sql.sqltypes.AutoString(length=512),
            nullable=True,
        ),
        sa.Column("invalidated_at", sa.DateTime(), nullable=True),
        sa.Column("invalidated_by_id", sa.Integer(), nullable=True),
        sa.Column("emailed_at", sa.DateTime(), nullable=True),
        sa.Column("emailed_to", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("emailed_by_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "expires_at > created_at",
            name="api_key_delivery_link_check_expires_after_created",
        ),
        sa.CheckConstraint(
            "(consumed_at IS NULL AND invalidated_at IS NULL) OR ciphertext IS NULL",
            name="api_key_delivery_link_check_dead_link_holds_no_secret",
        ),
        sa.ForeignKeyConstraint(["api_key_id"], ["apikey.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["user.id"]),
        sa.ForeignKeyConstraint(
            ["invalidated_by_id"], ["user.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["emailed_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_apikeydeliverylink_api_key_id"),
        "apikeydeliverylink",
        ["api_key_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_apikeydeliverylink_link_id"),
        "apikeydeliverylink",
        ["link_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_apikeydeliverylink_link_id"), table_name="apikeydeliverylink"
    )
    op.drop_index(
        op.f("ix_apikeydeliverylink_api_key_id"), table_name="apikeydeliverylink"
    )
    op.drop_table("apikeydeliverylink")
