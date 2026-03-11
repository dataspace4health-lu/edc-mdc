"""add area of competence

Revision ID: 9927f12c14ed
Revises: 295640220bd9
Create Date: 2025-01-29 10:15:01.137491

"""

from typing import Sequence, Union

from alembic import op
from alembic import op
from sqlalchemy import Column, VARCHAR, INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision: str = "9927f12c14ed"
down_revision: Union[str, None] = "295640220bd9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_area_of_competence",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("dataset_id", INTEGER(), ForeignKey("dataset.id"), nullable=False),
        Column(
            "key",
            VARCHAR(length=100),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_area_of_competence")
