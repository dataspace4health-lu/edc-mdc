"""add download_url to distribution

Revision ID: 91f4a9b5c144
Revises: bbefc9c96595
Create Date: 2025-04-24 15:00:21.212856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "91f4a9b5c144"
down_revision: Union[str, None] = "d081d3fb11ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column("download_url", sa.String(1000), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("distribution", "download_url")
