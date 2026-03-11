"""add bytesize and checksum

Revision ID: 2e574425106e
Revises: 3fc5c454c5c9
Create Date: 2025-04-16 14:27:40.034970

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2e574425106e"
down_revision: Union[str, None] = "3fc5c454c5c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column(
            "byte_size",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "distribution",
        sa.Column(
            "checksum",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("byte_size")
        batch_op.drop_column("checksum")
