"""Add main_group_id on building

Revision ID: abcd4d03111f
Revises: 4f74618478b5
Create Date: 2025-05-09 19:59:44.883843

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlmodel import Session, select, col

from server.models.database.building_db_model import Building
from server.models.database.group_classroom_link import GroupClassroomLink
from server.models.database.group_db_model import Group


# revision identifiers, used by Alembic.
revision: str = "abcd4d03111f"
down_revision: str | None = "4f74618478b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column("building", sa.Column("main_group_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_building_main_group", "building", "group", ["main_group_id"], ["id"]
    )

    statement = select(Building)
    buildings = session.exec(statement).all()
    for building in buildings:
        subquery = select(Group.id).where(col(GroupClassroomLink.group_id) == Group.id)
        statement = select(Group).where(
            col(Group.building_id) == building.id, ~sa.exists(subquery)
        )
        group = session.exec(statement).one()
        building.main_group_id = group.id
        session.add(building)

    session.commit()


def downgrade() -> None:
    op.drop_constraint("fk_building_main_group", "building", type_="foreignkey")
    op.drop_column("building", "main_group_id")
