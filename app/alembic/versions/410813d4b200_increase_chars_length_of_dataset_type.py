"""increase chars length of dataset_type

Revision ID: 410813d4b200
Revises: 6e172b621772
Create Date: 2025-04-08 23:06:08.382263

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "410813d4b200"
down_revision: Union[str, None] = "6e172b621772"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset_type") as batch_op:
        batch_op.alter_column(
            "key",
            existing_type=sa.String(length=100),
            type_=sa.String(length=255),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("dataset_type") as batch_op:
        batch_op.alter_column(
            "key",
            existing_type=sa.String(length=255),
            type_=sa.String(length=100),
            existing_nullable=False,
        )
