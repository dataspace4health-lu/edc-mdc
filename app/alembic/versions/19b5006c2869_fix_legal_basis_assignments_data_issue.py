"""fix legal basis assignments data issue

Revision ID: 19b5006c2869
Revises: 95f0d89a28a9
Create Date: 2025-08-26 14:28:01.154175

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "19b5006c2869"
down_revision: Union[str, None] = "95f0d89a28a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # remove any invalid assignments with keys that don't exist
    op.execute("""
        DELETE FROM legal_basis_assignments 
        WHERE legal_basis_key NOT IN (
            SELECT key FROM legal_basis WHERE key IS NOT NULL
        );
    """)


def downgrade() -> None:
    op.execute("DELETE FROM legal_basis_assignments")
