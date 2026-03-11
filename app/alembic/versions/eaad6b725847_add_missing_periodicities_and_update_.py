"""add missing periodicities and update cont

Revision ID: eaad6b725847
Revises: 7ead8ce3e8a6
Create Date: 2025-10-01 17:15:21.320650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "eaad6b725847"
down_revision: Union[str, None] = "7ead8ce3e8a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO periodicity (key, eng_label) VALUES
            ('https://publications.europa.eu/resource/authority/frequency/10MIN', 'every ten minutes'),
            ('https://publications.europa.eu/resource/authority/frequency/12HRS', 'every twelve hours'),
            ('https://publications.europa.eu/resource/authority/frequency/15MIN', 'every fifteen minutes'),
            ('https://publications.europa.eu/resource/authority/frequency/1MIN', 'every minute'),
            ('https://publications.europa.eu/resource/authority/frequency/30MIN', 'every thirty minutes'),
            ('https://publications.europa.eu/resource/authority/frequency/5MIN', 'every five minutes'),
            ('https://publications.europa.eu/resource/authority/frequency/AS_NEEDED', 'as needed'),
            ('https://publications.europa.eu/resource/authority/frequency/NOT_PLANNED', 'not planned'),
            ('https://publications.europa.eu/resource/authority/frequency/WEEKLY_5', 'five times a week');
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM periodicity
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/frequency/10MIN',
            'https://publications.europa.eu/resource/authority/frequency/12HRS',
            'https://publications.europa.eu/resource/authority/frequency/15MIN',
            'https://publications.europa.eu/resource/authority/frequency/1MIN',
            'https://publications.europa.eu/resource/authority/frequency/30MIN',
            'https://publications.europa.eu/resource/authority/frequency/5MIN',
            'https://publications.europa.eu/resource/authority/frequency/AS_NEEDED',
            'https://publications.europa.eu/resource/authority/frequency/NOT_PLANNED',
            'https://publications.europa.eu/resource/authority/frequency/WEEKLY_5'
        );
    """)
