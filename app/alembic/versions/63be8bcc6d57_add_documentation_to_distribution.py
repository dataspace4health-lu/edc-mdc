"""add documentation to distribution

Revision ID: 63be8bcc6d57
Revises: 38c9025d77ea
Create Date: 2025-04-14 11:22:47.335960

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "63be8bcc6d57"
down_revision: Union[str, None] = "38c9025d77ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "distribution",
        sa.Column(
            "documentation",
            sa.String(2048),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("distribution", "documentation")
