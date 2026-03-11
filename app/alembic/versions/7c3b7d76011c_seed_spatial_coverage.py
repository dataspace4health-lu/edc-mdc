"""seed spatial coverage

Revision ID: 7c3b7d76011c
Revises: 4cf90a6c0e02
Create Date: 2024-09-25 11:20:31.211576

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7c3b7d76011c"
down_revision: Union[str, None] = "4cf90a6c0e02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    INSERT INTO spatial_coverage (key, eng_label)
    VALUES
        ('https://publications.europa.eu/resource/authority/country/LUX', 'Luxembourg'),
        ('https://publications.europa.eu/resource/authority/country/FRA', 'France'),
        ('https://publications.europa.eu/resource/authority/country/DEU', 'Germany'),
        ('https://publications.europa.eu/resource/authority/country/BEL', 'Belgium'),
        ('https://publications.europa.eu/resource/authority/country/NLD', 'Netherlands')
    ON CONFLICT (key) DO NOTHING
    """)


def downgrade() -> None:
    pass
