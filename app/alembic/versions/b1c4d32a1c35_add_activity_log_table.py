"""add activity log table

Revision ID: b1c4d32a1c35
Revises: 43bd736a5584
Create Date: 2024-02-28 14:04:31.836926

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b1c4d32a1c35"
down_revision: Union[str, None] = "43bd736a5584"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_log",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
        sa.Column("action_type", sa.String, index=True),
        sa.Column("entity_type", sa.String, index=True),
        sa.Column("entity_id", sa.Integer),
        sa.Column("changes", sa.Text),
        sa.Column("timestamp", sa.DateTime, default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("activity_log")
