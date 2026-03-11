"""add modified_at to dataset

Revision ID: 80824d55d995
Revises: b8a9b7140f28
Create Date: 2023-10-25 15:19:56.180734

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "80824d55d995"
down_revision: Union[str, None] = "b8a9b7140f28"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column(
            "modified_at",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )
    op.execute("UPDATE dataset SET modified_at = submitted_at")


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("modified_at")
