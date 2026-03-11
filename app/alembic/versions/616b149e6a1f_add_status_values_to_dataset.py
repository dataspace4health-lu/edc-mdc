"""Add status values to dataset

Revision ID: 616b149e6a1f
Revises: 6cf1575b74e7
Create Date: 2024-06-06 17:13:36.429310

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "616b149e6a1f"
down_revision: Union[str, None] = "6cf1575b74e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE dataset SET status = 'Public catalogue';
        """)


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
