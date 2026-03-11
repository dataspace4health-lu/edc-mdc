"""add version change type to dataset

Revision ID: b7f436e5634a
Revises: 0fb3c5b81fc1
Create Date: 2026-02-10 16:49:22.450733

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b7f436e5634a"
down_revision: Union[str, None] = "0fb3c5b81fc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("version_change_type", sa.String(length=30), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_column("version_change_type")
