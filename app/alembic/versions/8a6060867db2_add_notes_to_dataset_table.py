"""Add notes to dataset table

Revision ID: 8a6060867db2
Revises: b6a228cf9217
Create Date: 2024-05-28 14:47:13.355638

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8a6060867db2"
down_revision: Union[str, None] = "b6a228cf9217"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("notes", sa.TEXT()))


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("notes")
