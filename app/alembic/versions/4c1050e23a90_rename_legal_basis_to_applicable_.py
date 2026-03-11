"""rename legal basis to applicable legislation

Revision ID: 4c1050e23a90
Revises: 20260212000000
Create Date: 2026-02-13 11:25:05.446518

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4c1050e23a90"
down_revision: Union[str, None] = "20260212000000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("legal_basis", "applicable_legislation")
    op.rename_table("legal_basis_assignments", "applicable_legislation_assignments")

    op.alter_column(
        "applicable_legislation_assignments",
        "legal_basis_key",
        new_column_name="applicable_legislation_key",
    )

    op.rename_table("dataset_legal_basis", "dataset_applicable_legislation")
    op.rename_table("distribution_legal_basis", "distribution_applicable_legislation")


def downgrade() -> None:
    op.rename_table("distribution_applicable_legislation", "distribution_legal_basis")
    op.rename_table("dataset_applicable_legislation", "dataset_legal_basis")
    op.alter_column(
        "applicable_legislation_assignments",
        "applicable_legislation_key",
        new_column_name="legal_basis_key",
    )
    op.rename_table("applicable_legislation_assignments", "legal_basis_assignments")
    op.rename_table("applicable_legislation", "legal_basis")
