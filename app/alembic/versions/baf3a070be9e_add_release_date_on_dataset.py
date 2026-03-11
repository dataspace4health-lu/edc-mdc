"""add release date on dataset

Revision ID: baf3a070be9e
Revises: 2e6c56fdc2b3
Create Date: 2025-05-12 11:46:07.107608

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "baf3a070be9e"
down_revision: Union[str, None] = "2e6c56fdc2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dataset", sa.Column("released_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("dataset", "released_at")
