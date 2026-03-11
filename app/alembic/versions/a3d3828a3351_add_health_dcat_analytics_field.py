"""add health dcat analytics field

Revision ID: a3d3828a3351
Revises: 63345c150c00
Create Date: 2026-01-20 13:56:30.371629

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a3d3828a3351"
down_revision: Union[str, None] = "63345c150c00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column("is_analytics", sa.Boolean(), default=False),
    )


def downgrade():
    op.drop_column("distribution", "is_analytics")
