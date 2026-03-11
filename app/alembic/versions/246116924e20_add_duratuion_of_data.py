"""add duratuion of data

Revision ID: 246116924e20
Revises: 2e8fba860fe2
Create Date: 2024-10-21 10:52:16.397265

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "246116924e20"
down_revision: Union[str, None] = "2e8fba860fe2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("duration_of_administrative_utility", sa.Integer))


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("duration_of_administrative_utility")
