"""remove sample

Revision ID: 3f073ddf8adf
Revises: baf3a070be9e
Create Date: 2025-05-13 14:39:17.646455

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3f073ddf8adf"
down_revision: Union[str, None] = "baf3a070be9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("distribution", "is_sample")


def downgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column(
            "is_sample", sa.Boolean(), server_default=sa.text("false"), nullable=True
        ),
    )
