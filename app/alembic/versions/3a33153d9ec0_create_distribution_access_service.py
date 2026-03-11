"""create distribution access service

Revision ID: 3a33153d9ec0
Revises: 4ada228d43e7
Create Date: 2025-04-29 10:09:20.879651

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3a33153d9ec0"
down_revision: Union[str, None] = "4ada228d43e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_access_service",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("distribution.id"),
            nullable=False,
        ),
        sa.Column(
            "data_service_id",
            sa.Integer(),
            sa.ForeignKey("data_service.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("distribution_access_service")
