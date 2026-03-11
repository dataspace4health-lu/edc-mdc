"""increase_eng_label_length_for_legal_basis_and_keyword

Revision ID: 7ead8ce3e8a6
Revises: 097e27d6bba3
Create Date: 2025-10-01 14:27:56.976825

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7ead8ce3e8a6"
down_revision: Union[str, None] = "097e27d6bba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the database dialect
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite doesn't support ALTER COLUMN, but it doesn't enforce VARCHAR length either
        # So we can skip the migration for SQLite
        pass
    else:
        # For PostgreSQL and other databases that support ALTER COLUMN
        op.alter_column(
            "legal_basis",
            "eng_label",
            existing_type=sa.String(100),
            type_=sa.String(500),
            existing_nullable=False,
        )

        op.alter_column(
            "keyword",
            "eng_label",
            existing_type=sa.String(100),
            type_=sa.String(500),
            existing_nullable=False,
        )


def downgrade() -> None:
    # Get the database dialect
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite doesn't support ALTER COLUMN, but it doesn't enforce VARCHAR length either
        # So we can skip the migration for SQLite
        pass
    else:
        # For PostgreSQL and other databases that support ALTER COLUMN
        op.alter_column(
            "legal_basis",
            "eng_label",
            existing_type=sa.String(500),
            type_=sa.String(100),
            existing_nullable=False,
        )

        op.alter_column(
            "keyword",
            "eng_label",
            existing_type=sa.String(500),
            type_=sa.String(100),
            existing_nullable=False,
        )
