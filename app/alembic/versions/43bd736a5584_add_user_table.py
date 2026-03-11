"""add user table

Revision ID: 43bd736a5584
Revises: 62acf83e5a26
Create Date: 2024-02-28 14:02:59.202122

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "43bd736a5584"
down_revision: Union[str, None] = "62acf83e5a26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    table = op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False, unique=True),
    )
    op.bulk_insert(
        table,
        [{"name": "system", "external_id": "system"}],
    )


def downgrade() -> None:
    op.drop_table("user")
