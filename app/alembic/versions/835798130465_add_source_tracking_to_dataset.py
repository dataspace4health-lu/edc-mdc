"""add source tracking to dataset

Revision ID: 835798130465
Revises: d60d7be94a5d
Create Date: 2025-11-05 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "835798130465"
down_revision: Union[str, None] = "d60d7be94a5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add source tracking columns
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "source",
                sa.String(50),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "source_dataset_id",
                sa.Integer(),
                nullable=True,
            )
        )

    # Create composite index for efficient lookups
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.create_index(
            "ix_dataset_source_lookup",
            ["source", "source_dataset_id"],
        )

    # Create unique constraint to prevent duplicate imports
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_dataset_source",
            ["source", "source_dataset_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_constraint("uq_dataset_source", type_="unique")
        batch_op.drop_index("ix_dataset_source_lookup")
        batch_op.drop_column("source_dataset_id")
        batch_op.drop_column("source")
