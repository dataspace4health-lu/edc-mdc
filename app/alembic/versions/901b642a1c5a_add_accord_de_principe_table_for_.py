"""add Accord de Principe table for distribution

Revision ID: 901b642a1c5a
Revises: 7cccc7f9a070
Create Date: 2025-06-03 14:22:54.475577

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, INTEGER, ForeignKey, VARCHAR

# revision identifiers, used by Alembic.
revision: str = "901b642a1c5a"
down_revision: Union[str, None] = "7cccc7f9a070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_accord_de_principe",
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
    op.drop_table("distribution_accord_de_principe")
