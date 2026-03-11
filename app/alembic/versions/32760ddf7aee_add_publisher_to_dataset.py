"""add publisher

Revision ID: 32760ddf7aee
Revises: 45c1837214a0
Create Date: 2023-11-20 13:48:47.919773

"""

from typing import Sequence, Union
from sqlalchemy import Column, VARCHAR
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32760ddf7aee"
down_revision: Union[str, None] = "45c1837214a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dataset", Column("publisher_name", VARCHAR(length=100)))


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
