"""insert health categories and themes values

Revision ID: cd00434d03c5
Revises: cf36a31e8186
Create Date: 2026-01-08 13:36:32.999962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cd00434d03c5"
down_revision: Union[str, None] = "cf36a31e8186"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO health_category (key, eng_label) VALUES
            ('EHRS', 'EHRS'),
            ('MRMR', 'MRMR'),
            ('HPML', 'HPML'),
            ('IDHP', 'IDHP'),
            ('RMMD', 'RMMD'),
            ('DIOH', 'DIOH'),
            ('RQSH', 'RQSH'),
            ('EMRD', 'EMRD'),
            ('EHCT', 'EHCT'),
            ('NRPE', 'NRPE'),
            ('PGEH', 'PGEH'),
            ('HGPD', 'HGPD'),
            ('EINS', 'EINS'),
            ('RPDG', 'RPDG'),
            ('HRAD', 'HRAD'),
            ('PHDR', 'PHDR'),
            ('WELA', 'WELA')
        ON CONFLICT (key) DO NOTHING;
    """)

    op.execute("""
        INSERT INTO health_theme (key, eng_label) VALUES
            ('CLIMATE_HEALTH', 'Climate Health'),
            ('ANTIMICROBIAL_CONTROL', 'Antimicrobial Control'),
            ('ENVIRONMENTAL_HEALTH', 'Environmental Health'),
            ('BLOOD_INFECTIONS', 'Blood Infections'),
            ('HEALTH_SYSTEMS', 'Health Systems'),
            ('SENSORY_HEALTH', 'Sensory Health'),
            ('RESPIRATORY_DISEASES', 'Respiratory Diseases'),
            ('LIFECOURSE_HEALTH', 'Lifecourse Health'),
            ('IMMUNIZATION_DISEASES', 'Immunization Diseases'),
            ('ENTERIC_INFECTIONS', 'Enteric Infections'),
            ('VECTOR_DISEASES', 'Vector Diseases'),
            ('REPRODUCTIVE_HEALTH', 'Reproductive Health'),
            ('NUTRITION_SECURITY', 'Nutrition Security'),
            ('NONCOMMUNICABLE_DISEASES', 'Noncommunicable Diseases'),
            ('TROPICAL_DISEASES', 'Tropical Diseases'),
            ('INJURY_PREVENTION', 'Injury Prevention'),
            ('EMERGENCY_SETTINGS', 'Emergency Settings'),
            ('CANCER_DISEASE', 'Cancer Disease'),
            ('HEALTH_PRODUCTS', 'Health Products'),
            ('MENTAL_HEALTH', 'Mental Health')
        ON CONFLICT (key) DO NOTHING;
    """)


def downgrade() -> None:
    pass
