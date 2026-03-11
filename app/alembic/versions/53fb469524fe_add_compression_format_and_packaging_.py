"""add compression format and packaging format

Revision ID: 53fb469524fe
Revises: e360b7d3246c
Create Date: 2025-04-17 11:47:09.829084

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "53fb469524fe"
down_revision: Union[str, None] = "e360b7d3246c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column(
            "compression_format",
            sa.String(2048),
            nullable=True,
        ),
    )
    op.add_column(
        "distribution",
        sa.Column(
            "packaging_format",
            sa.String(2048),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("distribution", "compression_format")
    op.drop_column("distribution", "packaging_format")
