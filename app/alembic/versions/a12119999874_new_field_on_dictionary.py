"""new field on dictionary

Revision ID: a12119999874
Revises: 9259ae346bf6
Create Date: 2025-05-06 15:35:20.343529

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a12119999874"
down_revision: Union[str, None] = "9259ae346bf6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_dictionary_entry",
        sa.Column("privacy_risk_type", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("privacy_risk_type")
