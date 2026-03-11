"""add temporal and spatial to dist

Revision ID: 5bb55604f61d
Revises: 025992cf158a
Create Date: 2025-04-25 10:18:24.171730

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5bb55604f61d"
down_revision: Union[str, None] = "025992cf158a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution", sa.Column("spatial_resolution", sa.Integer(), nullable=True)
    )
    op.add_column(
        "distribution", sa.Column("temporal_resolution", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("distribution", "spatial_resolution")
    op.drop_column("distribution", "temporal_resolution")
