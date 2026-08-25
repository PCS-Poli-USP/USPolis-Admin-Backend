"""fix userrole primary key

Revision ID: 761435876363
Revises: bf2fe3aee452
Create Date: 2026-07-17 22:04:10.620912

"""

from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "761435876363"
down_revision: str | None = "bf2fe3aee452"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # userrole.id was part of a 3-column composite primary key
    # (id, user_id, role_id) with no sequence/default on id, so nothing could
    # insert into this table without manually supplying a unique id. Table is
    # empty in every real environment, so this is a pure schema change.
    op.drop_constraint("userrole_pkey", "userrole", type_="primary")
    op.create_primary_key("userrole_pkey", "userrole", ["id"])
    op.execute("CREATE SEQUENCE userrole_id_seq OWNED BY userrole.id")
    op.execute(
        "ALTER TABLE userrole ALTER COLUMN id SET DEFAULT nextval('userrole_id_seq')"
    )
    op.execute(
        "SELECT setval('userrole_id_seq', COALESCE((SELECT MAX(id) FROM userrole), 1), false)"
    )
    op.create_unique_constraint("unique_user_role", "userrole", ["user_id", "role_id"])


def downgrade() -> None:
    op.drop_constraint("unique_user_role", "userrole", type_="unique")
    op.execute("ALTER TABLE userrole ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE userrole_id_seq")
    op.drop_constraint("userrole_pkey", "userrole", type_="primary")
    op.create_primary_key("userrole_pkey", "userrole", ["id", "user_id", "role_id"])
