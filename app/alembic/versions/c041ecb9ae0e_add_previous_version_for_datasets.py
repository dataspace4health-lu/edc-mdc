"""add previous version for datasets

Revision ID: c041ecb9ae0e
Revises: 3e4b3f66d11d
Create Date: 2025-07-08 10:45:35.268944

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c041ecb9ae0e"
down_revision: Union[str, None] = "3e4b3f66d11d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("previous_version_dataset_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_dataset_previous_version",
            "dataset",
            ["previous_version_dataset_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("dataset", schema=None) as batch_op:
        batch_op.drop_constraint("fk_dataset_previous_version", type_="foreignkey")
        batch_op.drop_column("previous_version_dataset_id")
