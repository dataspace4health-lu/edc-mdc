"""add legal basis table

Revision ID: 4c271ff581ed
Revises: 8f6b05d3114d
Create Date: 2024-11-12 09:31:04.400604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, VARCHAR

# revision identifiers, used by Alembic.
revision: str = "4c271ff581ed"
down_revision: Union[str, None] = "8f6b05d3114d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "legal_basis",
        Column("key", VARCHAR(length=100), primary_key=True, index=True),
        Column("eng_label", VARCHAR(length=100)),
    )


def downgrade() -> None:
    op.drop_table("legal_basis")
