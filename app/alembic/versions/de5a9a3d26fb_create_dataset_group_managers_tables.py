"""create dataset group managers tables

Revision ID: de5a9a3d26fb
Revises: b09e75a64c01
Create Date: 2024-11-14 15:03:09.224474

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "de5a9a3d26fb"
down_revision: Union[str, None] = "b09e75a64c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_group_managers",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "dataset_id",
            INTEGER(),
            ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "user_id",
            INTEGER(),
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_group_managers")
