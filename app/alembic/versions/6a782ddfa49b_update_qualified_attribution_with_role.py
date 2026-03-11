"""update qualified attribution with role

Revision ID: 6a782ddfa49b
Revises: 45943ce9a98f
Create Date: 2025-10-07 16:09:35.985165

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6a782ddfa49b"
down_revision: Union[str, None] = "45943ce9a98f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM dataset_qualified_attribution")

    with op.batch_alter_table("dataset_qualified_attribution", schema=None) as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(255), nullable=False))
        batch_op.create_index(
            "ix_dataset_qualified_attribution_dataset_id", ["dataset_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("dataset_qualified_attribution", schema=None) as batch_op:
        batch_op.drop_index("ix_dataset_qualified_attribution_dataset_id")
        batch_op.drop_column("role")
