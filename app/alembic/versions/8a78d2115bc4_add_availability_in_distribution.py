"""add availability in distribution

Revision ID: 8a78d2115bc4
Revises: d4ac0b8dadd9
Create Date: 2025-03-25 14:30:08.045412

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8a78d2115bc4"
down_revision: Union[str, None] = "d4ac0b8dadd9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("distribution", sa.Column("availability", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("distribution", "availability")
