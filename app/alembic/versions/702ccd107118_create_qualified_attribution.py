"""create qualified attribution

Revision ID: 702ccd107118
Revises: 3a33153d9ec0
Create Date: 2025-04-29 09:46:08.773265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "702ccd107118"
down_revision: Union[str, None] = "3a33153d9ec0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_qualified_attribution",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id", sa.INTEGER(), sa.ForeignKey("dataset.id"), nullable=False
        ),
        sa.Column(
            "organisation_id",
            sa.INTEGER(),
            sa.ForeignKey("organisations.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_qualified_attribution")
