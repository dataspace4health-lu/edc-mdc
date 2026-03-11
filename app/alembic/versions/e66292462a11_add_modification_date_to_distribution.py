"""add modification date to distribution

Revision ID: e66292462a11
Revises: 79811db73a21
Create Date: 2025-04-15 10:55:17.929835

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e66292462a11"
down_revision: Union[str, None] = "79811db73a21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column(
            "modification_date",
            sa.TIMESTAMP(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("modification_date")
