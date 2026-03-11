"""create other identifier and version notes tables

Revision ID: bbefc9c96595
Revises: c0e980255e81
Create Date: 2025-04-23 13:45:25.515920

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bbefc9c96595"
down_revision: Union[str, None] = "c0e980255e81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_other_identifier",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.INTEGER(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key",
            sa.String(),
            nullable=False,
        ),
    )

    op.create_table(
        "dataset_version_note",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.INTEGER(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key",
            sa.String(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_other_identifier")
    op.drop_table("dataset_version_note")
