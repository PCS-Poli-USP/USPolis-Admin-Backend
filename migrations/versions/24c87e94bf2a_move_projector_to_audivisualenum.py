"""Move projector to audivisualtype

Revision ID: 24c87e94bf2a
Revises: 4773a5364d80
Create Date: 2025-04-18 14:51:22.282956

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "24c87e94bf2a"
down_revision: str | None = "4773a5364d80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    audiovisual_type = sa.Enum("TV", "PROJECTOR", "NONE", name="audiovisualtype")
    audiovisual_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "classroom",
        sa.Column(
            "audiovisual",
            type_=audiovisual_type,
            nullable=True,
        ),
    )
    op.add_column(
        "class",
        sa.Column(
            "audiovisual",
            type_=audiovisual_type,
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE class SET audiovisual = CASE WHEN projector = TRUE THEN 'PROJECTOR'::audiovisualtype WHEN projector = FALSE THEN 'NONE'::audiovisualtype END"
    )
    op.execute(
        "UPDATE classroom SET audiovisual = CASE WHEN projector = TRUE THEN 'PROJECTOR'::audiovisualtype WHEN projector = FALSE THEN 'NONE'::audiovisualtype END"
    )

    op.drop_column("class", "projector")
    op.drop_column("classroom", "projector")

    op.alter_column("classroom", "audiovisual", nullable=False)
    op.alter_column("class", "audiovisual", nullable=False)


def downgrade() -> None:
    op.add_column(
        "classroom",
        sa.Column(
            "projector",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "class",
        sa.Column(
            "projector",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.execute(
        "UPDATE class SET projector = CASE WHEN audiovisual = 'PROJECTOR'::audiovisualtype THEN TRUE ELSE FALSE END"
    )
    op.execute(
        "UPDATE classroom SET projector = CASE WHEN audiovisual = 'PROJECTOR'::audiovisualtype THEN TRUE ELSE FALSE END"
    )

    op.drop_column("classroom", "audiovisual")
    op.drop_column("class", "audiovisual")
    op.execute("DROP TYPE public.audiovisualtype")
