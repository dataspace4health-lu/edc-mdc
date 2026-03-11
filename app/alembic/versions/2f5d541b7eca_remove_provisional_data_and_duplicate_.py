"""remove provisional data and duplicate entries from spatial_cov

Revision ID: 2f5d541b7eca
Revises: 27af3958fb04
Create Date: 2025-05-21 12:57:02.804878

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2f5d541b7eca"
down_revision: Union[str, None] = "27af3958fb04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM spatial_coverage
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/country/OP_DATPRO',
            'https://publications.europa.eu/resource/authority/country/XKX'
        )
        """)


def downgrade() -> None:
    pass
