"""add distribution path to dataset

Revision ID: b09e75a64c01
Revises: 70397f5696d2
Create Date: 2024-11-08 10:52:40.963211

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b09e75a64c01"
down_revision: Union[str, None] = "70397f5696d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column("distribution_path", sa.String(length=100), nullable=True),
    )


def downgrade():
    op.drop_column("distribution", "distribution_path")
