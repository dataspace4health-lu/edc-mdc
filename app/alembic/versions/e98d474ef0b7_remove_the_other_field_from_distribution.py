"""Remove the other field from distribution

Revision ID: e98d474ef0b7
Revises: a407fd1cef5c
Create Date: 2025-07-24 11:05:43.923573

"""

from typing import Sequence, Union
from sqlalchemy import Column, VARCHAR
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e98d474ef0b7"
down_revision: Union[str, None] = "a407fd1cef5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("distribution", "other_file_type_value")


def downgrade() -> None:
    op.add_column("distribution", Column("other_file_type_value", VARCHAR(length=100)))
