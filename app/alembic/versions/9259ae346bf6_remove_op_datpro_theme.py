"""remove OP_DATPRO theme

Revision ID: 9259ae346bf6
Revises: bd50c6f3f0fb
Create Date: 2025-05-05 17:12:04.593171

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9259ae346bf6"
down_revision: Union[str, None] = "bd50c6f3f0fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM theme WHERE key = 'OP_DATPRO'"))


def downgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "INSERT INTO theme (key, eng_label) VALUES ('OP_DATPRO', 'Provisional data')"
        )
    )
