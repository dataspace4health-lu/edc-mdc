"""remove_accord_de_principe_tables

Revision ID: eaaa28ceef9c
Revises: 835798130465
Create Date: 2025-11-19 15:43:30.075991

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "eaaa28ceef9c"
down_revision: Union[str, None] = "835798130465"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("dataset_accord_de_principe")
    op.drop_table("distribution_accord_de_principe")

    op.drop_table("accord_de_principe")


def downgrade() -> None:
    pass
