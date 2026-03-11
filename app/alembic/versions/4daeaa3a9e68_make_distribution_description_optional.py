"""make_distribution_description_optional

Revision ID: 4daeaa3a9e68
Revises: 172ce75e983e
Create Date: 2026-01-28 13:05:03.574209

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4daeaa3a9e68"
down_revision: Union[str, None] = "172ce75e983e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("distribution", schema=None) as batch_op:
        batch_op.alter_column("description", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    # Before making the column NOT NULL, we need to fill any NULL values with a default
    # This prevents the integrity error when reverting the migration
    op.execute(
        "UPDATE distribution SET description = 'No description provided' WHERE description IS NULL"
    )

    # Now we can safely make the column NOT NULL
    with op.batch_alter_table("distribution", schema=None) as batch_op:
        batch_op.alter_column("description", existing_type=sa.String(), nullable=False)
