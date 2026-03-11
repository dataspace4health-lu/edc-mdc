"""add list of countries in europe for spatial coverage

Revision ID: d7185550c9d2
Revises: 702ccd107118
Create Date: 2025-05-05 14:09:17.907190

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d7185550c9d2"
down_revision: Union[str, None] = "702ccd107118"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    INSERT INTO spatial_coverage (key, eng_label)
    VALUES
        ('https://publications.europa.eu/resource/authority/country/AUT', 'Austria'),
        ('https://publications.europa.eu/resource/authority/country/BGR', 'Bulgaria'),
        ('https://publications.europa.eu/resource/authority/country/CYP', 'Cyprus'),
        ('https://publications.europa.eu/resource/authority/country/CZE', 'Czechia'),
        ('https://publications.europa.eu/resource/authority/country/DNK', 'Denmark'),
        ('https://publications.europa.eu/resource/authority/country/EST', 'Estonia'),
        ('https://publications.europa.eu/resource/authority/country/FIN', 'Finland'),
        ('https://publications.europa.eu/resource/authority/country/HRV', 'Croatia'),
        ('https://publications.europa.eu/resource/authority/country/HUN', 'Hungary'),
        ('https://publications.europa.eu/resource/authority/country/IRL', 'Ireland'),
        ('https://publications.europa.eu/resource/authority/country/ITA', 'Italy'),
        ('https://publications.europa.eu/resource/authority/country/LTU', 'Lithuania'),
        ('https://publications.europa.eu/resource/authority/country/LVA', 'Latvia'),
        ('https://publications.europa.eu/resource/authority/country/MLT', 'Malta'),
        ('https://publications.europa.eu/resource/authority/country/POL', 'Poland'),
        ('https://publications.europa.eu/resource/authority/country/PRT', 'Portugal'),
        ('https://publications.europa.eu/resource/authority/country/ROU', 'Romania'),
        ('https://publications.europa.eu/resource/authority/country/SVK', 'Slovakia'),
        ('https://publications.europa.eu/resource/authority/country/SVN', 'Slovenia'),
        ('https://publications.europa.eu/resource/authority/country/ESP', 'Spain'),
        ('https://publications.europa.eu/resource/authority/country/SWE', 'Sweden')

    ON CONFLICT (key) DO NOTHING
    """)


def downgrade() -> None:
    pass
