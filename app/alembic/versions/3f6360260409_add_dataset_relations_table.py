"""add dataset relations table

Revision ID: 3f6360260409
Revises: 0a7b1c63c8be
Create Date: 2024-06-19 12:40:29.966204

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3f6360260409"
down_revision: Union[str, None] = "0a7b1c63c8be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_relation_entry",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "source_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("relation_type", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("dataset_relation_entry")
