"""add temporal restriction start and end

Revision ID: 68bce888fed1
Revises: c041ecb9ae0e
Create Date: 2025-07-08 19:23:46.014634

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "68bce888fed1"
down_revision: Union[str, None] = "c041ecb9ae0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column("temporal_restriction_start", sa.Date(), nullable=True),
    )
    op.add_column(
        "distribution",
        sa.Column("temporal_restriction_end", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("distribution", "temporal_restriction_end")
    op.drop_column("distribution", "temporal_restriction_start")
