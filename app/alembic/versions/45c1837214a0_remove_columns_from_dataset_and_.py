"""remove columns from dataset and distribution

Revision ID: 45c1837214a0
Revises: 80824d55d995
Create Date: 2023-11-16 16:11:53.149104

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "45c1837214a0"
down_revision: Union[str, None] = "80824d55d995"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("dataset_legal_frameworks")
    op.drop_table("legal_framework")
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("access_type")
    op.drop_table("access_type")


def downgrade() -> None:
    """
    This is an irreversible change.
    """
    pass
