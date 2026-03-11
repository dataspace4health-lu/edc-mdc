"""add languages to dataset

Revision ID: 189906a2e9ab
Revises: 410813d4b200
Create Date: 2025-04-09 11:07:41.522261

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "189906a2e9ab"
down_revision: Union[str, None] = "410813d4b200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_languages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id", sa.Integer(), sa.ForeignKey("dataset.id"), nullable=False
        ),
        sa.Column("key", sa.VARCHAR(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.id"],
        ),
        sa.ForeignKeyConstraint(
            ["key"],
            ["language.key"],
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_languages")
