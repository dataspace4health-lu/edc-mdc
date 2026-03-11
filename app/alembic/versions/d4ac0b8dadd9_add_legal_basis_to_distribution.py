"""add legal basis to distribution

Revision ID: d4ac0b8dadd9
Revises: 8d34466d194d
Create Date: 2025-03-14 07:45:55.699850

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "d4ac0b8dadd9"
down_revision: Union[str, None] = "8d34466d194d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_legal_basis",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "distribution_id", INTEGER(), ForeignKey("distribution.id"), nullable=False
        ),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("distribution_legal_basis")
