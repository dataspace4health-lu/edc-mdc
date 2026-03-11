"""create agent table

Revision ID: 933847526a5a
Revises: 6446648cebae
Create Date: 2024-09-12 16:18:31.880874

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "933847526a5a"
down_revision: Union[str, None] = "6446648cebae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
    )


def downgrade():
    op.drop_table("agents")
