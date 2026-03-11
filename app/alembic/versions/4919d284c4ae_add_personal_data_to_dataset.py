"""add personal data to dataset

Revision ID: 4919d284c4ae
Revises: ee76852469e0
Create Date: 2026-02-15 23:15:10.824448

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4919d284c4ae"
down_revision: Union[str, None] = "ee76852469e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_personal_data",
        sa.Column(
            "id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True
        ),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_dataset_personal_data_id"),
        "dataset_personal_data",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_dataset_personal_data_id"), table_name="dataset_personal_data"
    )
    op.drop_table("dataset_personal_data")
