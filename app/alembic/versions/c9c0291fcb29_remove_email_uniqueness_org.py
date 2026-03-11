"""remove email uniqueness org

Revision ID: c9c0291fcb29
Revises: fb474eb86ea6
Create Date: 2025-04-18 16:03:12.705742

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c9c0291fcb29"
down_revision: Union[str, None] = "fb474eb86ea6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("organisations", "email", unique=False)


def downgrade() -> None:
    op.alter_column("organisations", "email", unique=True)
