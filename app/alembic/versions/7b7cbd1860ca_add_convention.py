"""add convention

Revision ID: 7b7cbd1860ca
Revises: 246116924e20
Create Date: 2024-10-28 13:02:29.663971

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "7b7cbd1860ca"
down_revision: Union[str, None] = "246116924e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "dataset_conventions",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_conventions")
