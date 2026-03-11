"""add last login at

Revision ID: c3833b13fb06
Revises: a3d3828a3351
Create Date: 2026-01-21 16:18:57.291233

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3833b13fb06"
down_revision: Union[str, None] = "a3d3828a3351"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user", "last_login_at")
