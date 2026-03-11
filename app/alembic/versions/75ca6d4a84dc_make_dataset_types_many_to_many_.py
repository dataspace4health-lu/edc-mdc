"""make_dataset_types_many_to_many_relationship

Revision ID: 75ca6d4a84dc
Revises: 9400f1c734f0
Create Date: 2024-05-14 08:55:28.504684

"""

import os
from typing import Sequence, Union

from alembic import op
from sqlalchemy import INTEGER, VARCHAR, Column, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "75ca6d4a84dc"
down_revision: Union[str, None] = "9400f1c734f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_types",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key", VARCHAR(length=100), ForeignKey("dataset_type.key"), nullable=False
        ),
    )

    op.execute("""
        INSERT INTO dataset_types (dataset_id, key) 
        SELECT id, dataset_type 
        FROM dataset
        WHERE dataset_type IS NOT NULL
        """)

    if not is_dev_or_test_env():
        op.drop_column("dataset", "dataset_type")


def downgrade() -> None:
    op.drop_table("dataset_types")
    if not is_dev_or_test_env():
        op.add_column("dataset", "dataset_type")


def is_dev_or_test_env() -> bool:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    return ENVIRONMENT == "development" or ENVIRONMENT == "test"
