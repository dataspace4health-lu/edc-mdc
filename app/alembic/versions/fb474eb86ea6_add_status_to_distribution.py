"""add status to distribution

Revision ID: fb474eb86ea6
Revises: 53fb469524fe
Create Date: 2025-04-17 14:02:42.579451

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fb474eb86ea6"
down_revision: Union[str, None] = "53fb469524fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column("distribution_dcat_status", sa.String(100), nullable=True),
    )


def downgrade():
    op.drop_column("distribution", "distribution_dcat_status")
