"""add population coverage to health dcat compliant dataset

Revision ID: 7f6924e7f809
Revises: 21f2dac11276
Create Date: 2026-01-14 14:26:15.142491

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7f6924e7f809"
down_revision: Union[str, None] = "21f2dac11276"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dataset", sa.Column("population_coverage", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("dataset", "population_coverage")
