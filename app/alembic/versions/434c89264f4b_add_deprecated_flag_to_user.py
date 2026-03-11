"""add deprecated flag to user

Revision ID: 434c89264f4b
Revises: cfd71dad620c
Create Date: 2025-08-19 08:30:29.867589

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "434c89264f4b"
down_revision: Union[str, None] = "cfd71dad620c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "is_deprecated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "is_deprecated")
