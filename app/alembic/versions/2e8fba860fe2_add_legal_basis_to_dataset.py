"""add legal basis to dataset

Revision ID: 2e8fba860fe2
Revises: a760cfd55499
Create Date: 2024-10-14 10:15:14.095922

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "2e8fba860fe2"
down_revision: Union[str, None] = "a760cfd55499"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_legal_basis",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_legal_basis")
