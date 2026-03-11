"""add dataset qualified relations table

Revision ID: c74b9d1d74ea
Revises: 5bb55604f61d
Create Date: 2025-04-28 10:49:28.747042

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c74b9d1d74ea"
down_revision: Union[str, None] = "5bb55604f61d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_qualified_relation",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "source_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("qualified_relation_url", sa.String(2048), nullable=False),
        sa.Column("qualified_relation_role", sa.String, nullable=True),
        sa.Column("qualified_relation_description", sa.Text, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("dataset_qualified_relation")
