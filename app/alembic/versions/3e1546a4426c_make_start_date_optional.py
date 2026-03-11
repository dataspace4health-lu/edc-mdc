"""make start date optional

Revision ID: 3e1546a4426c
Revises: fa8a4ddfc2d0
Create Date: 2026-01-28 16:30:56.249523

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3e1546a4426c"
down_revision: Union[str, None] = "fa8a4ddfc2d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.alter_column(
            "time_period_start", existing_type=sa.Date(), nullable=True
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.alter_column(
            "time_period_start", existing_type=sa.Date(), nullable=False
        )
