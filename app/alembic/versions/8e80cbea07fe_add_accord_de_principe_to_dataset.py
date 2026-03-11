"""add Accord de Principe to dataset

Revision ID: 8e80cbea07fe
Revises: 95d0edeb890f
Create Date: 2025-06-03 11:03:19.189719

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "8e80cbea07fe"
down_revision: Union[str, None] = "95d0edeb890f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_accord_de_principe",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_accord_de_principe")
