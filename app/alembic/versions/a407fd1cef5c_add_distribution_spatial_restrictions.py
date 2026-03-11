"""add distribution spatial restrictions

Revision ID: a407fd1cef5c
Revises: 059885578885
Create Date: 2025-07-15 16:14:07.624830

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a407fd1cef5c"
down_revision: Union[str, None] = "059885578885"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_spatial_restrictions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("distribution.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "key",
            sa.String,
            sa.ForeignKey("spatial_coverage.key"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("distribution_spatial_restrictions")
