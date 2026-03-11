"""rename archived_at to deprecated_at

Revision ID: 3e4b3f66d11d
Revises: aa0cdccdcaf9
Create Date: 2025-07-01 11:40:21.682576

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3e4b3f66d11d"
down_revision: Union[str, None] = "aa0cdccdcaf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for broad compatibility
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.alter_column(
            "archived_at",
            new_column_name="deprecated_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.alter_column(
            "deprecated_at",
            new_column_name="archived_at",
            existing_type=sa.DateTime(timezone=True),
            existing_nullable=True,
        )
