"""Update subject type and user model

Revision ID: d41e4f7ca46f
Revises: 4beb4f0ff6d7
Create Date: 2025-04-02 19:27:34.419064

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from server.utils.brazil_datetime import BrazilDatetime


# revision identifiers, used by Alembic.
revision: str = "d41e4f7ca46f"
down_revision: str | None = "4beb4f0ff6d7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        UPDATE public.subject 
        SET type = 'OTHER' 
        WHERE type IS NULL
    """)
    op.execute('ALTER TYPE public."subjecttype" RENAME TO subjecttype_old')

    new_type = sa.Enum(
        "BIANNUAL", "FOUR_MONTHLY", "OTHER", "POSTGRADUATE", name="subjecttype"
    )
    new_type.create(op.get_bind(), checkfirst=False)
    op.alter_column(
        "subject",
        "type",
        type_=new_type,
        nullable=False,
        schema="public",
        postgresql_using="type::text::subjecttype",
    )
    op.execute("DROP TYPE public.subjecttype_old")
    # op.execute("COMMIT")

    op.add_column("user", sa.Column("last_visited", sa.DateTime(), nullable=True))
    now = BrazilDatetime.now_utc()
    op.execute(f"UPDATE \"user\" SET last_visited = '{now}' WHERE last_visited IS NULL")
    op.alter_column("user", "last_visited", nullable=False)


def downgrade() -> None:
    op.execute("""
        UPDATE public.subject 
        SET type = 'OTHER' 
        WHERE type = 'POSTGRADUATE'
    """)
    op.execute('ALTER TYPE public."subjecttype" RENAME TO subjecttype_old')
    old_type = sa.Enum("BIANNUAL", "FOUR_MONTHLY", "OTHER", name="subjecttype")
    old_type.create(op.get_bind(), checkfirst=False)
    op.alter_column(
        "subject",
        "type",
        type_=old_type,
        nullable=True,
        schema="public",
        postgresql_using="type::text::subjecttype",
    )
    op.execute("DROP TYPE public.subjecttype_old")
    op.drop_column("user", "last_visited")
