"""remove provisional data from themes

Revision ID: 2e6c56fdc2b3
Revises: 9f312da81c05
Create Date: 2025-05-08 16:46:35.251268

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2e6c56fdc2b3"
down_revision: Union[str, None] = "9f312da81c05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "DELETE FROM theme WHERE key = 'https://publications.europa.eu/resource/authority/data-theme/OP_DATPRO'"
        )
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "INSERT INTO theme (key, eng_label) VALUES ('https://publications.europa.eu/resource/authority/data-theme/OP_DATPRO', 'Provisional data')"
        )
    )
