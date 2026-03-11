"""update data protection

Revision ID: 4d91690e1a67
Revises: 5941b1ac2386
Create Date: 2025-01-08 10:07:08.906114

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "4d91690e1a67"
down_revision: Union[str, None] = "5941b1ac2386"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "dataset_data_protection_types",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )

    op.execute("""
        INSERT INTO dataset_data_protection_types (dataset_id, key)
        SELECT id, data_protection_type
        FROM dataset 
        WHERE data_protection_type IS NOT NULL
    """)

    op.drop_column("dataset", "data_protection_type")


def downgrade() -> None:
    op.drop_table("dataset_data_protection_types")
    op.drop_table("data_protection_types")
