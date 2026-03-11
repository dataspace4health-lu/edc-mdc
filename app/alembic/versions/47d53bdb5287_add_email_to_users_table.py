"""add email to users table

Revision ID: 47d53bdb5287
Revises: b1c4d32a1c35
Create Date: 2024-03-12 13:50:30.808993

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, String

# revision identifiers, used by Alembic.
revision: str = "47d53bdb5287"
down_revision: Union[str, None] = "b1c4d32a1c35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", Column("email", String(255)))


def downgrade() -> None:
    op.drop_column("user", "email")
