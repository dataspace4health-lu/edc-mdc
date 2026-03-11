"""add data protection type to dataset

Revision ID: 69b0ffd30aab
Revises: 4d917c225f2b
Create Date: 2024-11-20 20:10:52.476305

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "69b0ffd30aab"
down_revision: Union[str, None] = "4d917c225f2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column("data_protection_type", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dataset", "data_protection_type")
