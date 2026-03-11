"""add is deprecated to source authentique label

Revision ID: 3d3559ffe62c
Revises: 0a3b14d62967
Create Date: 2025-08-04 15:26:26.581118

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3d3559ffe62c"
down_revision: Union[str, None] = "0a3b14d62967"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "authentic_source_label",
        sa.Column(
            "is_deprecated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("authentic_source_label", "is_deprecated")
