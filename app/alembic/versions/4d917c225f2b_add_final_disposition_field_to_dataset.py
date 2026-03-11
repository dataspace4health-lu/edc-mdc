"""add final disposition field to dataset

Revision ID: 4d917c225f2b
Revises: de5a9a3d26fb
Create Date: 2024-11-20 15:25:52.956434

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4d917c225f2b"
down_revision: Union[str, None] = "de5a9a3d26fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("dataset", sa.Column("final_disposition", sa.String(), nullable=True))


def downgrade():
    op.drop_column("dataset", "final_disposition")
