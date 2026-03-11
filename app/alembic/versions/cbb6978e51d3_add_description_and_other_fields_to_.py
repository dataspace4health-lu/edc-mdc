"""add description and other fields to legal bases

Revision ID: cbb6978e51d3
Revises: 9927f12c14ed
Create Date: 2025-01-24 16:17:30.965118

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cbb6978e51d3"
down_revision: Union[str, None] = "9927f12c14ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("legal_basis", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("legal_basis", sa.Column("link", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("legal_basis", "link")
    op.drop_column("legal_basis", "description")
