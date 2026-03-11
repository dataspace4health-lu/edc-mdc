"""add media type to distribution

Revision ID: 8cfebf7df489
Revises: 2e574425106e
Create Date: 2025-04-16 11:40:15.189449

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8cfebf7df489"
down_revision: Union[str, None] = "2e574425106e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column(
            "media_type",
            sa.String(2048),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("distribution", "media_type")
