"""create spatial and temporal resolutions

Revision ID: c0e980255e81
Revises: 4d2296b77908
Create Date: 2025-04-23 13:43:20.618174

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c0e980255e81"
down_revision: Union[str, None] = "4d2296b77908"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "dataset",
        sa.Column("spatial_resolution", sa.Integer(), nullable=True),
    )

    op.add_column(
        "dataset",
        sa.Column("temporal_resolution", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_column("dataset", "spatial_resolution")
    op.drop_column("dataset", "temporal_resolution")
