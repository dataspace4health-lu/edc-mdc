"""add has_code_values to dataset

Revision ID: a6e802a257a6
Revises: 20260128143723
Create Date: 2026-02-06 15:14:08.038313

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a6e802a257a6"
down_revision: Union[str, None] = "279a24d3cb68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dataset", sa.Column("has_code_values", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("dataset", "has_code_values")
