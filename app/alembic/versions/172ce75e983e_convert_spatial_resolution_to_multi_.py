"""Convert spatial resolution to multi-value association tables

Revision ID: 172ce75e983e
Revises: 0ea3e1d4f5f8
Create Date: 2026-01-21 14:43:45.293937

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "172ce75e983e"
down_revision: Union[str, None] = "0ea3e1d4f5f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create association table for multi-value spatial resolution (dataset only)
    op.create_table(
        "dataset_spatial_resolution",
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dataset_id", "value"),
    )

    # Migrate existing data to new table
    connection = op.get_bind()

    # Migrate dataset spatial resolution
    result = connection.execute(
        sa.text(
            "SELECT id, spatial_resolution FROM dataset WHERE spatial_resolution IS NOT NULL"
        )
    )
    for row in result:
        connection.execute(
            sa.text(
                "INSERT INTO dataset_spatial_resolution (dataset_id, value) VALUES (:dataset_id, :value)"
            ),
            {"dataset_id": row[0], "value": row[1]},
        )

    # Drop old column from dataset only
    op.drop_column("dataset", "spatial_resolution")


def downgrade() -> None:
    # Restore single-value column for dataset
    op.add_column(
        "dataset", sa.Column("spatial_resolution", sa.Integer(), nullable=True)
    )

    # Migrate data back (use first value if multiple exist)
    connection = op.get_bind()

    result = connection.execute(
        sa.text(
            "SELECT dataset_id, MIN(value) FROM dataset_spatial_resolution GROUP BY dataset_id"
        )
    )
    for row in result:
        connection.execute(
            sa.text("UPDATE dataset SET spatial_resolution = :value WHERE id = :id"),
            {"value": row[1], "id": row[0]},
        )

    # Drop association table
    op.drop_table("dataset_spatial_resolution")
