"""add dataset series

Revision ID: daf55ee82545
Revises: c9c0291fcb29
Create Date: 2025-04-22 14:56:06.320603

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "daf55ee82545"
down_revision: Union[str, None] = "c9c0291fcb29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dataset",
        sa.Column(
            "is_dataset_series", sa.Boolean(), nullable=False, server_default="False"
        ),
    )

    op.create_table(
        "series_memberships",
        sa.Column(
            "id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True
        ),
        sa.Column(
            "series_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("is_first", sa.Boolean(), nullable=False, server_default="False"),
        sa.Column("is_last", sa.Boolean(), nullable=False, server_default="False"),
        sa.UniqueConstraint("series_id", "dataset_id", name="uq_series_membership"),
    )


def downgrade() -> None:
    op.drop_table("series_memberships")
    op.drop_column("dataset", "is_dataset_series")
