"""merge dataset relations into single unified table

Revision ID: d2e2b77ef800
Revises: eaad6b725847
Create Date: 2025-09-30 13:34:56.278503

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d2e2b77ef800"
down_revision: Union[str, None] = "eaad6b725847"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_relation",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "source_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("external_url", sa.String(2048), nullable=True),
        sa.Column("external_role", sa.String, nullable=True),
        sa.Column("external_description", sa.Text, nullable=True),
        sa.Column("relation_type", sa.String, nullable=True),
    )

    op.execute("""
        INSERT INTO dataset_relation 
            (source_dataset, target_dataset, relation_type)
        SELECT 
            source_dataset, target_dataset, relation_type
        FROM dataset_relation_entry
    """)

    op.drop_table("dataset_relation_entry")


def downgrade() -> None:
    op.create_table(
        "dataset_relation_entry",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "source_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_dataset",
            sa.Integer,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("relation_type", sa.String, nullable=False),
    )

    op.execute("""
        INSERT INTO dataset_relation_entry 
            (source_dataset, target_dataset, relation_type)
        SELECT 
            source_dataset, target_dataset, relation_type
        FROM dataset_relation
        WHERE target_dataset IS NOT NULL
    """)

    op.drop_table("dataset_relation")
