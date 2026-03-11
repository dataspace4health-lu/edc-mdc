"""add dataset comments

Revision ID: 70397f5696d2
Revises: 4c271ff581ed
Create Date: 2024-11-13 09:30:20.347653

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, VARCHAR, TEXT, DateTime, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "70397f5696d2"
down_revision: Union[str, None] = "4c271ff581ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_comments",
        Column("id", Integer, primary_key=True, index=True, autoincrement=True),
        Column(
            "dataset_id",
            Integer,
            ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "user_id",
            Integer,
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("content", TEXT, nullable=False),
        Column("timestamp", DateTime, default=sa.func.now()),
    )
    op.create_index(
        "idx_dataset_comments_dataset_id", "dataset_comments", ["dataset_id"]
    )
    op.create_index("idx_dataset_comments_user_id", "dataset_comments", ["user_id"])


def downgrade() -> None:
    op.drop_table("dataset_comments")
