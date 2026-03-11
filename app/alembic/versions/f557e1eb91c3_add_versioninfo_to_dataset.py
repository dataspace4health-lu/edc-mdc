"""Add versionInfo to dataset

Revision ID: f557e1eb91c3
Revises: 3f6360260409
Create Date: 2024-07-12 10:57:18.983399

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f557e1eb91c3"
down_revision: Union[str, None] = "3f6360260409"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("version", sa.String))


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("version")
