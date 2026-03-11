"""Add has policy to distribution

Revision ID: 3fc5c454c5c9
Revises: a80a05cee846
Create Date: 2025-04-16 11:13:24.672849

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3fc5c454c5c9"
down_revision: Union[str, None] = "a80a05cee846"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "distribution", sa.Column("policy_type", sa.String(100), nullable=True)
    )
    op.add_column(
        "distribution", sa.Column("policy_action_type", sa.String(100), nullable=True)
    )
    op.add_column(
        "distribution",
        sa.Column("policy_constraint_type", sa.String(100), nullable=True),
    )
    op.add_column(
        "distribution",
        sa.Column("policy_constraint_value", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("distribution", "policy_constraint_value")
    op.drop_column("distribution", "policy_constraint_type")
    op.drop_column("distribution", "policy_action_type")
    op.drop_column("distribution", "policy_type")
