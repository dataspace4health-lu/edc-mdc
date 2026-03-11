"""Add spatial coverage to dataset

Revision ID: 726963ba4f5f
Revises: f557e1eb91c3
Create Date: 2024-07-19 14:35:05.189366

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "726963ba4f5f"
down_revision: Union[str, None] = "f557e1eb91c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "spatial_coverage",
        Column("key", VARCHAR(length=100), primary_key=True, index=True),
        Column("eng_label", VARCHAR(length=100)),
    )

    op.create_table(
        "dataset_spatial_coverages",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            ForeignKey("spatial_coverage.key"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_spatial_coverages")
    op.drop_table("spatial_coverage")
