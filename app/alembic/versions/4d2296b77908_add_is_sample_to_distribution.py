"""add is sample to distribution

Revision ID: 4d2296b77908
Revises: c9c0291fcb29
Create Date: 2025-04-22 13:37:05.149793

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4d2296b77908"
down_revision: Union[str, None] = "daf55ee82545"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column("is_sample", sa.Boolean(), default=False),
    )


def downgrade():
    op.drop_column("distribution", "is_sample")
