"""add retention period field to dataset

Revision ID: 63345c150c00
Revises: 7f6924e7f809
Create Date: 2026-01-16 11:07:51.420281

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "63345c150c00"
down_revision: Union[str, None] = "7f6924e7f809"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add retention_period_start and retention_period_end columns to dataset table
    op.add_column(
        "dataset", sa.Column("retention_period_start", sa.Date(), nullable=True)
    )
    op.add_column(
        "dataset", sa.Column("retention_period_end", sa.Date(), nullable=True)
    )


def downgrade() -> None:
    # Remove retention_period_end and retention_period_start columns from dataset table
    op.drop_column("dataset", "retention_period_end")
    op.drop_column("dataset", "retention_period_start")
