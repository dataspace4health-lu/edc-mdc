"""add distribution.other_file_type_value column

Revision ID: cb3b2f00acab
Revises: 5912261dd8af
Create Date: 2023-10-12 15:30:58.836169

"""

from typing import Sequence, Union
from sqlalchemy import Column, VARCHAR
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cb3b2f00acab"
down_revision: Union[str, None] = "5912261dd8af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("distribution", Column("other_file_type_value", VARCHAR(length=100)))


def downgrade() -> None:
    op.drop_column("distribution", "other_file_type_value")
