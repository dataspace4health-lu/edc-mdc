"""rename roles to iam_roles

Revision ID: 1d9ba57b845f
Revises: ba51732d08b1
Create Date: 2025-06-02 08:33:01.588409

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1d9ba57b845f"
down_revision: Union[str, None] = "ba51732d08b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "roles",
            new_column_name="iam_roles",
            existing_type=sa.String(),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "iam_roles",
            new_column_name="roles",
            existing_type=sa.String(),
            existing_nullable=True,
        )
