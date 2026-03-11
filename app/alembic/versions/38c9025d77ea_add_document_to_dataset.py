"""add document to dataset

Revision ID: 38c9025d77ea
Revises: b909662313cd
Create Date: 2025-04-14 11:21:54.123249

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "38c9025d77ea"
down_revision: Union[str, None] = "b909662313cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "dataset",
        sa.Column(
            "documentation",
            sa.String(2048),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("dataset", "documentation")
