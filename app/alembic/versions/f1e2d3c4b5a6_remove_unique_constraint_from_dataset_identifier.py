"""remove unique constraint from dataset identifier

Revision ID: f1e2d3c4b5a6
Revises: 6a782ddfa49b
Create Date: 2025-10-15 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f1e2d3c4b5a6"
down_revision: Union[str, None] = "6a782ddfa49b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("uq_dataset_identifier", type_="unique")


def downgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.create_unique_constraint("uq_dataset_identifier", ["identifier"])
