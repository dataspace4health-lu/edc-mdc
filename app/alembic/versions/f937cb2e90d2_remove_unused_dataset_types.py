"""remove_unused_dataset_types

Revision ID: f937cb2e90d2
Revises: eaaa28ceef9c
Create Date: 2025-11-20 16:49:58.404521

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f937cb2e90d2"
down_revision: Union[str, None] = "eaaa28ceef9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO dataset_type (key, eng_label) VALUES
            ('https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA', 'Structured data'),
            ('https://publications.europa.eu/resource/authority/dataset-type/REPORT', 'Report'),
            ('https://publications.europa.eu/resource/authority/resource-type/DATAPAPER', 'DataPaper'),
            ('https://publications.europa.eu/resource/authority/dataset-type/MODEL', 'Model'),
            ('https://publications.europa.eu/resource/authority/dataset-type/AUDIOVISUAL', 'Audiovisual'),
            ('https://publications.europa.eu/resource/authority/dataset-type/IMAGE', 'Image'),
            ('https://publications.europa.eu/resource/authority/dataset-type/TEXT', 'Text'),
            ('https://publications.europa.eu/resource/authority/dataset-type/STATISTICAL_DATA', 'Statistical data')
        ON CONFLICT (key) DO NOTHING;
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA'
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/dataset-type/DATASET',
            'https://publications.europa.eu/resource/authority/dataset-type/ARCHIVED_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/CONFIGURATION_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/DATABASES',
            'https://publications.europa.eu/resource/authority/resource-type/RAW_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_TEXT'
        );
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/REPORT'
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/resource-type/DISSERTATION',
            'https://publications.europa.eu/resource/authority/dataset-type/OUTPUTMANAGEMENTPLAN'
        );
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/resource-type/DATAPAPER'
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/dataset-type/JOURNALARCTICLE',
            'https://publications.europa.eu/resource/authority/resource-type/PREPRINT',
            'https://publications.europa.eu/resource/authority/resource-type/STUDYREGISTRATION'
        );
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/MODEL'
        WHERE key = 'https://publications.europa.eu/resource/authority/dataset-type/STANDARD';
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/AUDIOVISUAL'
        WHERE key = 'https://publications.europa.eu/resource/authority/resource-type/AUDTIOVISUAL_DATA';
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/IMAGE'
        WHERE key = 'https://publications.europa.eu/resource/authority/dataset-type/IMAGES';
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/TEXT'
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/dataset-type/NETWORKBASED_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/PLAIN_TEXT',
            'https://publications.europa.eu/resource/authority/dataset-type/STANDARD_OFFICE_DOCUMENTS'
        );
    """)

    op.execute("""
        UPDATE dataset_types
        SET key = 'https://publications.europa.eu/resource/authority/dataset-type/STATISTICAL_DATA'
        WHERE key = 'https://publications.europa.eu/resource/authority/dataset-type/SCIENTIFIC_AND_STATISTICAL_DATA_FORMATS';
    """)

    # Remove duplicates - keep only one of each (dataset_id, key) pair
    op.execute("""
        DELETE FROM dataset_types
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM dataset_types
            GROUP BY dataset_id, key
        );
    """)

    op.execute("""
        DELETE FROM dataset_type
        WHERE key IN (
            'https://publications.europa.eu/resource/authority/dataset-type/DATASET',
            'https://publications.europa.eu/resource/authority/resource-type/DISSERTATION',
            'https://publications.europa.eu/resource/authority/dataset-type/JOURNALARCTICLE',
            'https://publications.europa.eu/resource/authority/dataset-type/OUTPUTMANAGEMENTPLAN',
            'https://publications.europa.eu/resource/authority/resource-type/PREPRINT',
            'https://publications.europa.eu/resource/authority/dataset-type/STANDARD',
            'https://publications.europa.eu/resource/authority/resource-type/STUDYREGISTRATION',
            'https://publications.europa.eu/resource/authority/dataset-type/ARCHIVED_DATA',
            'https://publications.europa.eu/resource/authority/resource-type/AUDTIOVISUAL_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/CONFIGURATION_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/DATABASES',
            'https://publications.europa.eu/resource/authority/dataset-type/IMAGES',
            'https://publications.europa.eu/resource/authority/dataset-type/NETWORKBASED_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/PLAIN_TEXT',
            'https://publications.europa.eu/resource/authority/resource-type/RAW_DATA',
            'https://publications.europa.eu/resource/authority/dataset-type/SCIENTIFIC_AND_STATISTICAL_DATA_FORMATS',
            'https://publications.europa.eu/resource/authority/dataset-type/STANDARD_OFFICE_DOCUMENTS',
            'https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_TEXT'
        );
    """)


def downgrade() -> None:
    op.execute("""
        INSERT INTO dataset_type (key, eng_label) VALUES
            ('https://publications.europa.eu/resource/authority/dataset-type/DATASET', 'Dataset'),
            ('https://publications.europa.eu/resource/authority/resource-type/DISSERTATION', 'Dissertation'),
            ('https://publications.europa.eu/resource/authority/dataset-type/JOURNALARCTICLE', 'JournalArticle'),
            ('https://publications.europa.eu/resource/authority/dataset-type/OUTPUTMANAGEMENTPLAN', 'OutputManagementPlan'),
            ('https://publications.europa.eu/resource/authority/resource-type/PREPRINT', 'Preprint'),
            ('https://publications.europa.eu/resource/authority/dataset-type/STANDARD', 'Standard'),
            ('https://publications.europa.eu/resource/authority/resource-type/STUDYREGISTRATION', 'StudyRegistration'),
            ('https://publications.europa.eu/resource/authority/dataset-type/ARCHIVED_DATA', 'Archived data'),
            ('https://publications.europa.eu/resource/authority/resource-type/AUDTIOVISUAL_DATA', 'Audiovisual data'),
            ('https://publications.europa.eu/resource/authority/dataset-type/CONFIGURATION_DATA', 'Configuration data'),
            ('https://publications.europa.eu/resource/authority/dataset-type/DATABASES', 'Databases'),
            ('https://publications.europa.eu/resource/authority/dataset-type/IMAGES', 'Images'),
            ('https://publications.europa.eu/resource/authority/dataset-type/NETWORKBASED_DATA', 'Networkbased data'),
            ('https://publications.europa.eu/resource/authority/dataset-type/PLAIN_TEXT', 'Plain text'),
            ('https://publications.europa.eu/resource/authority/resource-type/RAW_DATA', 'Raw data'),
            ('https://publications.europa.eu/resource/authority/dataset-type/SCIENTIFIC_AND_STATISTICAL_DATA_FORMATS', 'Scientific and statistical data formats'),
            ('https://publications.europa.eu/resource/authority/dataset-type/STANDARD_OFFICE_DOCUMENTS', 'Standard office documents'),
            ('https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_TEXT', 'Structured text');
    """)

    op.execute("""
        DELETE FROM dataset_type
        WHERE key = 'https://publications.europa.eu/resource/authority/dataset-type/STRUCTURED_DATA';
    """)
