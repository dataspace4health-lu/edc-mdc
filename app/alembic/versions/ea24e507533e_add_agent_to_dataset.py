"""add agent to dataset

Revision ID: ea24e507533e
Revises: 933847526a5a
Create Date: 2024-09-12 16:41:00.335063

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ea24e507533e"
down_revision: Union[str, None] = "933847526a5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(sa.Column("agent_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_dataset_agent",  # Name of the foreign key constraint
            "agents",  # Referenced table
            ["agent_id"],  # Local column in the dataset table
            ["id"],  # Referenced column in the agents table
        )


def downgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_constraint("fk_dataset_agent", type_="foreignkey")
        batch_op.drop_column("agent_id")
