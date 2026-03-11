"""migrate status from archived to deprecated

Revision ID: 53c07ffd649f
Revises: 51638ab7bc82
Create Date: 2025-10-13 10:02:51.329956

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "53c07ffd649f"
down_revision: Union[str, None] = "51638ab7bc82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE dataset
        SET status = 'DEPRECATED'
        WHERE status = 'ARCHIVED'
        """)


def downgrade() -> None:
    op.execute("""
        UPDATE dataset
        SET status = 'ARCHIVED'
        WHERE status = 'DEPRECATED'
        """)
