"""rename specific to monitoring location

Revision ID: 45943ce9a98f
Revises: 53c07ffd649f
Create Date: 2025-10-13 15:53:29.637034

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "45943ce9a98f"
down_revision: Union[str, None] = "53c07ffd649f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.alter_column(
            "specific_location",
            new_column_name="monitoring_location",
            existing_type=sa.String(length=100),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.alter_column(
            "monitoring_location",
            new_column_name="specific_location",
            existing_type=sa.String(length=100),
            existing_nullable=True,
        )
