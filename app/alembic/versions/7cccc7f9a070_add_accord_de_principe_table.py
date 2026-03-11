"""add Accord de Principe table

Revision ID: 7cccc7f9a070
Revises: 8e80cbea07fe
Create Date: 2025-06-03 11:07:16.738240

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, VARCHAR, Text, Integer

# revision identifiers, used by Alembic.
revision: str = "7cccc7f9a070"
down_revision: Union[str, None] = "8e80cbea07fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "accord_de_principe",
        Column("key", VARCHAR(length=100), primary_key=True, index=True),
        Column("eng_label", VARCHAR(length=100)),
        Column("description", Text, nullable=True),
        Column("link", Text, nullable=True),
        Column("created_by_id", Integer(), sa.ForeignKey("user.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("accord_de_principe")
