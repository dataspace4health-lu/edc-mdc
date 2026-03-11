"""Add authentic source reviewed to dataset

Revision ID: aa0cdccdcaf9
Revises: f9f356c7af9c
Create Date: 2025-07-01 19:05:06.532796

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "aa0cdccdcaf9"
down_revision: Union[str, None] = "f9f356c7af9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column(
            "authentic_source_reviewed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("datasets", "authentic_source_reviewed_at")
