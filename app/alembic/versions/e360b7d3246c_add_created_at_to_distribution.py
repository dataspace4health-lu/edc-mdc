"""add created_at to distribution

Revision ID: e360b7d3246c
Revises: 8cfebf7df489
Create Date: 2025-04-17 10:51:07.519441

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e360b7d3246c"
down_revision: Union[str, None] = "8cfebf7df489"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("distribution", "created_at")
