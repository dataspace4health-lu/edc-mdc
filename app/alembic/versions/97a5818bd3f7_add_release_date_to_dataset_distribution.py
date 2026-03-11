"""add release date to dataset & distribution

Revision ID: 97a5818bd3f7
Revises: 3f073ddf8adf
Create Date: 2025-05-13 14:47:00.800294

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "97a5818bd3f7"
down_revision: Union[str, None] = "3f073ddf8adf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column(
            "release_date",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )
    op.add_column(
        "distribution",
        sa.Column(
            "release_date",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("release_date")
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("release_date")
