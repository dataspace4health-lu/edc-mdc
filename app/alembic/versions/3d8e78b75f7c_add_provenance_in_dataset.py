"""add provenance in dataset

Revision ID: 3d8e78b75f7c
Revises: 8a78d2115bc4
Create Date: 2025-03-26 12:23:55.718805

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3d8e78b75f7c"
down_revision: Union[str, None] = "8a78d2115bc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("dataset", sa.Column("provenance", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("dataset", "provenance")
