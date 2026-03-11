"""Add parent_key column to keyword table for keyword nesting

Revision ID: 91947dc479dc
Revises: 47d53bdb5287
Create Date: 2024-04-23 17:55:04.823905

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "91947dc479dc"
down_revision: Union[str, None] = "47d53bdb5287"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("keyword") as batch_op:
        batch_op.add_column(
            sa.Column("parent_key", sa.VARCHAR(length=100), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_keyword_parent_key",
            "keyword",
            ["parent_key"],
            ["key"],
        )


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
