"""add health dcat nr of records and nr of unique individuals

Revision ID: 21f2dac11276
Revises: 790aee5e94bb
Create Date: 2026-01-13 14:16:26.310254

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "21f2dac11276"
down_revision: Union[str, None] = "790aee5e94bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("number_of_records", sa.Integer))
        batch_op.add_column(sa.Column("number_of_unique_individuals", sa.Integer))


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("number_of_records")
        batch_op.drop_column("number_of_unique_individuals")
