"""add dataset area of work

Revision ID: 295640220bd9
Revises: af7feed2fa72
Create Date: 2025-01-22 11:55:23.541532

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "295640220bd9"
down_revision: Union[str, None] = "af7feed2fa72"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_area_of_work",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_area_of_work")
