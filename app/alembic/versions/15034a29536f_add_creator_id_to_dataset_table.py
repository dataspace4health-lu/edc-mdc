"""Add creator_id to Dataset table

Revision ID: 15034a29536f
Revises: 3bbc159d3691
Create Date: 2024-05-17 14:20:08.335764

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "15034a29536f"
down_revision: Union[str, None] = "3bbc159d3691"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("creator_id", sa.Integer))
        batch_op.create_foreign_key("fk_creator_id", "user", ["creator_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("fk_creator_id", type_="foreignkey")
        batch_op.drop_column("creator_id")
