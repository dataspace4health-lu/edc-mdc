"""Add InternalOnly to Distribution Table

Revision ID: 9400f1c734f0
Revises: 91947dc479dc
Create Date: 2024-05-10 13:40:36.949287

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9400f1c734f0"
down_revision: Union[str, None] = "91947dc479dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column("internal_only", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("distribution", "internal_only")
