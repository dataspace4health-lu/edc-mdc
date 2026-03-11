"""add coding system field to dataset

Revision ID: ee76852469e0
Revises: 4f8204722c78
Create Date: 2026-02-12 14:16:25.136732

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ee76852469e0"
down_revision: Union[str, None] = "4f8204722c78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_coding_systems",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("dataset_coding_systems")
