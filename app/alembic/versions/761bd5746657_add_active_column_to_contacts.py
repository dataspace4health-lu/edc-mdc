"""add is deprecated column to contacts

Revision ID: 761bd5746657
Revises: 2b5bac03003e
Create Date: 2025-07-30 17:09:44.688494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "761bd5746657"
down_revision: Union[str, None] = "2b5bac03003e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "contacts",
        sa.Column(
            "is_deprecated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
    )


def downgrade():
    op.drop_column("contacts", "is_deprecated")
