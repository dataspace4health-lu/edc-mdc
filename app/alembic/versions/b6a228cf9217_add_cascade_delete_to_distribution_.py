"""Add cascade delete to distribution_languages

Revision ID: b6a228cf9217
Revises: 15034a29536f
Create Date: 2024-05-27 12:53:40.993719

"""

import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b6a228cf9217"
down_revision: Union[str, None] = "15034a29536f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not is_dev_or_test_env():
        with op.batch_alter_table("distribution_languages", schema=None) as batch_op:
            batch_op.drop_constraint(
                "distribution_languages_distribution_id_fkey", type_="foreignkey"
            )
            batch_op.create_foreign_key(
                "distribution_languages_distribution_id_cascade_fkey",
                "distribution",
                ["distribution_id"],
                ["id"],
                ondelete="CASCADE",
            )


def downgrade() -> None:
    if not is_dev_or_test_env():
        with op.batch_alter_table("distribution_languages", schema=None) as batch_op:
            batch_op.drop_constraint(
                "distribution_languages_distribution_id_cascade_fkey",
                type_="foreignkey",
            )
            batch_op.create_foreign_key(
                "distribution_languages_distribution_id_fkey",
                "distribution",
                ["distribution_id"],
                ["id"],
            )


def is_dev_or_test_env() -> bool:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    return ENVIRONMENT == "development" or ENVIRONMENT == "test"
