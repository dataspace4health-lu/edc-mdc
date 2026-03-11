"""remove representation_technique table

Revision ID: 5912261dd8af
Revises: 3139e4925542
Create Date: 2023-10-11 13:37:05.208409

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5912261dd8af"
down_revision: Union[str, None] = "3139e4925542"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("representation_technique")
    op.drop_table("representation_technique")


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
