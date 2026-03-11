"""Add notes to distribution table

Revision ID: cac830252894
Revises: 8a6060867db2
Create Date: 2024-05-29 14:23:19.019074

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cac830252894"
down_revision: Union[str, None] = "8a6060867db2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(sa.Column("notes", sa.TEXT()))


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("notes")
