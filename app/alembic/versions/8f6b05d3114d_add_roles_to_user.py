"""add roles to user

Revision ID: 8f6b05d3114d
Revises: da98930f2e91
Create Date: 2024-11-06 19:30:07.255065

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8f6b05d3114d"
down_revision: Union[str, None] = "da98930f2e91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("roles", sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column("user", "roles")
