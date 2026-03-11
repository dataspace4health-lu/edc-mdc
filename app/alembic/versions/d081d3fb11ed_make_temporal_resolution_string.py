"""make temporal resolution string

Revision ID: d081d3fb11ed
Revises: bbefc9c96595
Create Date: 2025-04-24 15:04:02.217418

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d081d3fb11ed"
down_revision: Union[str, None] = "bbefc9c96595"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("dataset", "temporal_resolution")
    op.add_column("dataset", sa.Column("temporal_resolution", sa.String()))


def downgrade() -> None:
    op.drop_column("dataset", "temporal_resolution")
    op.add_column("dataset", sa.Column("temporal_resolution", sa.Integer()))
