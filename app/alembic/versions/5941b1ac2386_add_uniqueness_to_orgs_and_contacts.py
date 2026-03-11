"""add uniqueness to orgs and contacts

Revision ID: 5941b1ac2386
Revises: 7925f697704a
Create Date: 2024-12-17 15:30:03.524022

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5941b1ac2386"
down_revision: Union[str, None] = "7925f697704a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("organisations", "name", unique=True)
    op.alter_column("organisations", "email", unique=True)

    op.alter_column("contacts", "name", unique=True)
    op.alter_column("contacts", "email", unique=True)


def downgrade():
    op.alter_column("organisations", "name", unique=False)
    op.alter_column("organisations", "email", unique=False)

    op.alter_column("contacts", "name", unique=False)
    op.alter_column("contacts", "email", unique=False)
