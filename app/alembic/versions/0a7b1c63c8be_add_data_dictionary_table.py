"""add data dictionary table

Revision ID: 0a7b1c63c8be
Revises: 6cf1575b74e7
Create Date: 2024-06-06 16:27:16.921799

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0a7b1c63c8be"
down_revision: Union[str, None] = "616b149e6a1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_dictionary_entry",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column("field_name", sa.String, nullable=False, index=True),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("data_type", sa.String, nullable=False),
        sa.Column("table_name", sa.String, nullable=False),
        sa.Column("dataset_id", sa.Integer, sa.ForeignKey("dataset.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("data_dictionary_entry")
