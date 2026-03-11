"""add specific location to dataset

Revision ID: 7925f697704a
Revises: 69b0ffd30aab
Create Date: 2024-12-09 12:49:31.709967

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7925f697704a"
down_revision: Union[str, None] = "69b0ffd30aab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "dataset",
        sa.Column("specific_location", sa.String(length=100), nullable=True),
    )


def downgrade():
    op.drop_column("dataset", "specific_location")
