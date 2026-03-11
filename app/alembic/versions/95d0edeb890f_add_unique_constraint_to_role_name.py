"""Add unique constraint to role.name

Revision ID: 95d0edeb890f
Revises: 1d9ba57b845f
Create Date: 2025-06-02 11:39:42.379986

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "95d0edeb890f"
down_revision: Union[str, None] = "1d9ba57b845f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("role") as batch_op:
        batch_op.create_unique_constraint("unique_role_name", ["name"])


def downgrade() -> None:
    with op.batch_alter_table("role") as batch_op:
        batch_op.drop_constraint("unique_role_name", type_="unique")
