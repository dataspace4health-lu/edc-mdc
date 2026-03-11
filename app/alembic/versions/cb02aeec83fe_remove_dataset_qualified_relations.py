"""Remove dataset qualified relations

Revision ID: cb02aeec83fe
Revises: 19b5006c2869
Create Date: 2025-09-15 08:32:18.546322

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cb02aeec83fe"
down_revision: Union[str, None] = "19b5006c2869"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("dataset_qualified_relation")


def downgrade() -> None:
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
