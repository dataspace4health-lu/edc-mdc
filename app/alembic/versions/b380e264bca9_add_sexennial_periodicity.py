"""add sexennial periodicity

Revision ID: b380e264bca9
Revises: 6391a2b4a895
Create Date: 2026-02-23 10:36:04.336797

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b380e264bca9"
down_revision: Union[str, None] = "6391a2b4a895"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO periodicity (key, eng_label)
        VALUES (
            'http://publications.europa.eu/resource/authority/frequency/SEXENNIAL',
            'sexennial'
        )
        ON CONFLICT (key) DO NOTHING
        """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM periodicity
        WHERE key = 'http://publications.europa.eu/resource/authority/frequency/SEXENNIAL'
        """)
