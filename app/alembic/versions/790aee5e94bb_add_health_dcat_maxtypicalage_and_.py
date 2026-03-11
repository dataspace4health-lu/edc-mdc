"""add health dcat maxTypicalAge and minTypicalAge

Revision ID: 790aee5e94bb
Revises: cd00434d03c5
Create Date: 2026-01-08 11:39:33.809467

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "790aee5e94bb"
down_revision: Union[str, None] = "cd00434d03c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("max_typical_age", sa.Integer))
        batch_op.add_column(sa.Column("min_typical_age", sa.Integer))


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("max_typical_age")
        batch_op.drop_column("min_typical_age")
