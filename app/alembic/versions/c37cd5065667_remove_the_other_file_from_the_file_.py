"""Remove the other-file from the file_type table

Revision ID: c37cd5065667
Revises: e98d474ef0b7
Create Date: 2025-07-24 11:33:57.292837

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c37cd5065667"
down_revision: Union[str, None] = "e98d474ef0b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "DELETE FROM file_type WHERE key = 'OTHER' AND NOT EXISTS (SELECT 1 FROM distribution WHERE file_type = 'OTHER')"
        )
    )


def downgrade() -> None:
    pass
