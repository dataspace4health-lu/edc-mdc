"""create data service and endpoint tables

Revision ID: 4ada228d43e7
Revises: c74b9d1d74ea
Create Date: 2025-04-28 10:49:09.801526

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4ada228d43e7"
down_revision: Union[str, None] = "c74b9d1d74ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_service",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "title",
            sa.String(),
            nullable=False,
        ),
    )

    op.create_table(
        "data_service_endpoint",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "data_service_id",
            sa.INTEGER(),
            sa.ForeignKey("data_service.id"),
            nullable=False,
        ),
        sa.Column(
            "endpoint_url",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "endpoint_description",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("data_service_endpoint")
    op.drop_table("data_service")
