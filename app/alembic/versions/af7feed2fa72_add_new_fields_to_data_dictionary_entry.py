"""add new fields to data dictionary entry

Revision ID: af7feed2fa72
Revises: 5941b1ac2386
Create Date: 2025-01-03 14:44:23.207219

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "af7feed2fa72"
down_revision: Union[str, None] = "4d91690e1a67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_dictionary_entry",
        sa.Column("personally_identifiable_variable", sa.Boolean, nullable=True),
    )
    op.add_column(
        "data_dictionary_entry", sa.Column("required", sa.Boolean, nullable=True)
    )
    op.add_column(
        "data_dictionary_entry", sa.Column("max_allowed_value", sa.Float, nullable=True)
    )
    op.add_column(
        "data_dictionary_entry", sa.Column("min_allowed_value", sa.Float, nullable=True)
    )
    op.add_column(
        "data_dictionary_entry", sa.Column("variable_unit", sa.String, nullable=True)
    )
    op.add_column(
        "data_dictionary_entry", sa.Column("allowed_values", sa.String, nullable=True)
    )
    op.add_column(
        "data_dictionary_entry",
        sa.Column("allowed_values_description", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("data_dictionary_entry", "personally_identifiable_variable")
    op.drop_column("data_dictionary_entry", "required")
    op.drop_column("data_dictionary_entry", "max_allowed_value")
    op.drop_column("data_dictionary_entry", "min_allowed_value")
    op.drop_column("data_dictionary_entry", "variable_unit")
    op.drop_column("data_dictionary_entry", "allowed_values")
    op.drop_column("data_dictionary_entry", "allowed_values_description")
