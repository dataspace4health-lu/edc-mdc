"""add is deprecated for organisations

Revision ID: 0a3b14d62967
Revises: 761bd5746657
Create Date: 2025-08-07 09:38:23.340401

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0a3b14d62967"
down_revision: Union[str, None] = "761bd5746657"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organisations",
        sa.Column(
            "is_deprecated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("organisations", "is_deprecated")
