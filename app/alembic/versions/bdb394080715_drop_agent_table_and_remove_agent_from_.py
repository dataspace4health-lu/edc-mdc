"""Drop agent table and remove agent from database

Revision ID: bdb394080715
Revises: 12f226499e6c
Create Date: 2024-10-06 12:55:21.752463

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bdb394080715"
down_revision: Union[str, None] = "1775e34ed43c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_constraint("fk_dataset_agent", type_="foreignkey")
        batch_op.drop_column("agent_id")

    op.drop_table("agents")


def downgrade():
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
    )

    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(sa.Column("agent_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_dataset_agent",
            "agents",
            ["agent_id"],
            ["id"],
        )
