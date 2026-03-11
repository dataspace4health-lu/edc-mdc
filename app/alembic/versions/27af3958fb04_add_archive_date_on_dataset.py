"""add archive date on dataset

Revision ID: 27af3958fb04
Revises: 4f7d3c4bed7d
Create Date: 2025-05-16 13:59:46.551872

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "27af3958fb04"
down_revision: Union[str, None] = "105f161a7c65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("dataset", "archived_at")
