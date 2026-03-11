"""add position field to data dictionary entry

Revision ID: 7ac7d043807e
Revises: f937cb2e90d2
Create Date: 2025-11-21 12:33:20.912701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7ac7d043807e"
down_revision: Union[str, None] = "f937cb2e90d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add nullable position column to data_dictionary_entry
    op.add_column(
        "data_dictionary_entry", sa.Column("position", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    # Drop position column
    op.drop_column("data_dictionary_entry", "position")
