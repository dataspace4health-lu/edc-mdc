"""remove dataset_type_other_value from dataset table

Revision ID: 6e172b621772
Revises: 3d8e78b75f7c
Create Date: 2025-04-07 17:33:17.031750

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6e172b621772"
down_revision: Union[str, None] = "3d8e78b75f7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("dataset", "dataset_type_other_value")


def downgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column("dataset_type_other_value", sa.VARCHAR(length=100), nullable=True),
    )
