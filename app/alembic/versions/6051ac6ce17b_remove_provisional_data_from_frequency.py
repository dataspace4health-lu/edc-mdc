"""remove provisional data from frequency

Revision ID: 6051ac6ce17b
Revises: 97a5818bd3f7
Create Date: 2025-05-14 12:02:40.691895

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6051ac6ce17b"
down_revision: Union[str, None] = "70ccccb6f8f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "DELETE FROM periodicity WHERE key = 'https://publications.europa.eu/resource/authority/frequency/OP_DATPRO'"
        )
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "INSERT INTO periodicity (key, eng_label) VALUES ('https://publications.europa.eu/resource/authority/frequency/OP_DATPRO', 'Provisional data')"
        )
    )
