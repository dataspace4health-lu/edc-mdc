"""remove topics table

Revision ID: 3139e4925542
Revises: 5125bedce7b8
Create Date: 2023-10-11 13:22:44.635122

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3139e4925542"
down_revision: Union[str, None] = "5125bedce7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("dataset_topics")
    op.drop_table("topic")


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
