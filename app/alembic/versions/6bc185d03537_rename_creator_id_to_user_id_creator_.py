"""Rename creator_id to user_id, creator_name to contact_name, and contact_point to contact_email

Revision ID: 6bc185d03537
Revises: e8e35f1a4eb7
Create Date: 2024-08-27 13:36:47.671071

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6bc185d03537"
down_revision: Union[str, None] = "726963ba4f5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("dataset", "creator_id", new_column_name="user_id")
    op.alter_column("dataset", "creator_name", new_column_name="contact_name")
    op.alter_column("dataset", "creator_email", new_column_name="contact_email")


def downgrade() -> None:
    op.alter_column("dataset", "user_id", new_column_name="creator_id")
    op.alter_column("dataset", "contact_name", new_column_name="creator_name")
    op.alter_column("dataset", "contact_email", new_column_name="creator_email")
