"""add health legal basis to dataset

Revision ID: 4f8204722c78
Revises: ef4d1f56fa65
Create Date: 2026-02-16 16:05:15.574338

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4f8204722c78"
down_revision: Union[str, None] = "ef4d1f56fa65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_health_legal_basis_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dataset_health_legal_basis_entries_id"),
        "dataset_health_legal_basis_entries",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_dataset_health_legal_basis_entries_id"),
        table_name="dataset_health_legal_basis_entries",
    )
    op.drop_table("dataset_health_legal_basis_entries")
