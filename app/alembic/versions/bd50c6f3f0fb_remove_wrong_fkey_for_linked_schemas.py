"""remove wrong fkey for linked schemas

Revision ID: bd50c6f3f0fb
Revises: d7185550c9d2
Create Date: 2025-05-06 14:36:06.432936

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bd50c6f3f0fb"
down_revision: Union[str, None] = "d7185550c9d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "new_distribution_linked_schema",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("distribution.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key",
            sa.String(),
            nullable=False,
        ),
    )

    op.execute("""
        INSERT INTO new_distribution_linked_schema (id, distribution_id, key)
        SELECT id, distribution_id, key FROM distribution_linked_schema
    """)

    op.drop_table("distribution_linked_schema")
    op.rename_table("new_distribution_linked_schema", "distribution_linked_schema")


def downgrade() -> None:
    op.create_table(
        "old_distribution_linked_schema",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key",
            sa.String(),
            nullable=False,
        ),
    )

    op.execute("""
        INSERT INTO old_distribution_linked_schema (id, distribution_id, key)
        SELECT id, distribution_id, key FROM distribution_linked_schema
    """)

    op.drop_table("distribution_linked_schema")
    op.rename_table("old_distribution_linked_schema", "distribution_linked_schema")
