"""Add creator to dataset

Revision ID: f32f99e75110
Revises: 6bc185d03537
Create Date: 2024-08-27 17:21:46.216024

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f32f99e75110"
down_revision: Union[str, None] = "6bc185d03537"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("dataset", sa.Column("creator", sa.String(), nullable=True))


def downgrade():
    op.drop_column("dataset", "creator")
