"""add_category_and_accessible_within_ctie_to_organisation

Revision ID: d60d7be94a5d
Revises: f1e2d3c4b5a6
Create Date: 2025-10-20 22:47:22.515478

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d60d7be94a5d"
down_revision: Union[str, None] = "f1e2d3c4b5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add category column (optional string field for EP/OSP classification)
    op.add_column("organisations", sa.Column("category", sa.String(), nullable=True))

    # Add accessible_within_ctie column (optional boolean for CTIE network access)
    op.add_column(
        "organisations",
        sa.Column("accessible_within_ctie", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    # Remove the columns in reverse order
    op.drop_column("organisations", "accessible_within_ctie")
    op.drop_column("organisations", "category")
