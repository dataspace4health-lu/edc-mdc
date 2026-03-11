"""make periodicities recommended

Revision ID: fa8a4ddfc2d0
Revises: 4daeaa3a9e68
Create Date: 2026-01-28 14:10:45.141184

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fa8a4ddfc2d0"
down_revision: Union[str, None] = "4daeaa3a9e68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.alter_column("periodicity", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.alter_column("periodicity", existing_type=sa.String(), nullable=False)
