"""add landing page to dataset

Revision ID: b909662313cd
Revises: 189906a2e9ab
Create Date: 2025-04-10 16:51:10.697286

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b909662313cd"
down_revision: Union[str, None] = "189906a2e9ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "dataset",
        sa.Column(
            "landing_page",
            sa.String(2048),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("dataset", "landing_page")
