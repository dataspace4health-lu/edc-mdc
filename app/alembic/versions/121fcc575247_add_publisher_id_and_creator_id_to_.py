"""Add publisher_id and creator_id to dataset

Revision ID: 121fcc575247
Revises: bdb394080715
Create Date: 2024-10-06 13:06:51.105608

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "121fcc575247"
down_revision: Union[str, None] = "bdb394080715"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("publisher_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("creator_id", sa.Integer(), nullable=True))

        batch_op.create_foreign_key(
            "fk_publisher_id",
            "organisations",
            ["publisher_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("fk_publisher_id", type_="foreignkey")

        batch_op.drop_column("publisher_id")
        batch_op.drop_column("creator_id")
