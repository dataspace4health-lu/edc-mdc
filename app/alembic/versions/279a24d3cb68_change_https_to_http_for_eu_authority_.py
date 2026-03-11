"""change_https_to_http_for_eu_authority_urls

Revision ID: 279a24d3cb68
Revises: 20260128143723
Create Date: 2026-01-30 14:30:32.801220

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "279a24d3cb68"
down_revision: Union[str, None] = "20260128143723"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update all EU authority URLs from https to http
    # Strategy: Insert new HTTP rows, update references, delete old HTTPS rows
    # This avoids foreign key constraint violations without special permissions

    # STEP 1: Insert duplicate rows with HTTP URLs in lookup tables

    # Insert HTTP versions in theme table
    op.execute("""
        INSERT INTO theme (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM theme
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTP versions in periodicity table
    op.execute("""
        INSERT INTO periodicity (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM periodicity
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTP versions in file_type table
    op.execute("""
        INSERT INTO file_type (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM file_type
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTP versions in language table
    op.execute("""
        INSERT INTO language (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM language
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTP versions in dataset_type table
    op.execute("""
        INSERT INTO dataset_type (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM dataset_type
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTP versions in spatial_coverage table
    op.execute("""
        INSERT INTO spatial_coverage (key, eng_label)
        SELECT 
            REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/'),
            eng_label
        FROM spatial_coverage
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # STEP 2: Update all foreign key references to use HTTP URLs

    # Update dataset_themes junction table
    op.execute("""
        UPDATE dataset_themes 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update dataset_types junction table
    op.execute("""
        UPDATE dataset_types 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update dataset_languages junction table
    op.execute("""
        UPDATE dataset_languages 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update dataset_spatial_coverages junction table
    op.execute("""
        UPDATE dataset_spatial_coverages 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update distribution_languages junction table
    op.execute("""
        UPDATE distribution_languages 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update dataset table - rights_statement and periodicity fields
    op.execute("""
        UPDATE dataset 
        SET rights_statement = REPLACE(rights_statement, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE rights_statement LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    op.execute("""
        UPDATE dataset 
        SET periodicity = REPLACE(periodicity, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE periodicity LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update distribution table - rights_statement and file_type fields
    op.execute("""
        UPDATE distribution 
        SET rights_statement = REPLACE(rights_statement, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE rights_statement LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    op.execute("""
        UPDATE distribution 
        SET file_type = REPLACE(file_type, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE file_type LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Update distribution_spatial_restrictions table
    op.execute("""
        UPDATE distribution_spatial_restrictions 
        SET key = REPLACE(key, 'https://publications.europa.eu/resource/authority/', 'http://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # STEP 3: Delete old HTTPS rows from lookup tables

    # Delete HTTPS rows from theme table
    op.execute("""
        DELETE FROM theme 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTPS rows from periodicity table
    op.execute("""
        DELETE FROM periodicity 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTPS rows from file_type table
    op.execute("""
        DELETE FROM file_type 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTPS rows from language table
    op.execute("""
        DELETE FROM language 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTPS rows from dataset_type table
    op.execute("""
        DELETE FROM dataset_type 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTPS rows from spatial_coverage table
    op.execute("""
        DELETE FROM spatial_coverage 
        WHERE key LIKE 'https://publications.europa.eu/resource/authority/%'
        """)


def downgrade() -> None:
    # Revert all EU authority URLs from http back to https
    # Strategy: Insert HTTPS rows, update references, delete HTTP rows

    # STEP 1: Insert duplicate rows with HTTPS URLs in lookup tables

    # Insert HTTPS versions in theme table
    op.execute("""
        INSERT INTO theme (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM theme
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTPS versions in periodicity table
    op.execute("""
        INSERT INTO periodicity (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM periodicity
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTPS versions in file_type table
    op.execute("""
        INSERT INTO file_type (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM file_type
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTPS versions in language table
    op.execute("""
        INSERT INTO language (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM language
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTPS versions in dataset_type table
    op.execute("""
        INSERT INTO dataset_type (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM dataset_type
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # Insert HTTPS versions in spatial_coverage table
    op.execute("""
        INSERT INTO spatial_coverage (key, eng_label)
        SELECT 
            REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/'),
            eng_label
        FROM spatial_coverage
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        ON CONFLICT (key) DO NOTHING
        """)

    # STEP 2: Update all foreign key references to use HTTPS URLs

    # Revert dataset_themes junction table
    op.execute("""
        UPDATE dataset_themes 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert dataset_types junction table
    op.execute("""
        UPDATE dataset_types 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert dataset_languages junction table
    op.execute("""
        UPDATE dataset_languages 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert dataset_spatial_coverages junction table
    op.execute("""
        UPDATE dataset_spatial_coverages 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert distribution_languages junction table
    op.execute("""
        UPDATE distribution_languages 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert dataset table
    op.execute("""
        UPDATE dataset 
        SET rights_statement = REPLACE(rights_statement, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE rights_statement LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    op.execute("""
        UPDATE dataset 
        SET periodicity = REPLACE(periodicity, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE periodicity LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert distribution table
    op.execute("""
        UPDATE distribution 
        SET rights_statement = REPLACE(rights_statement, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE rights_statement LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    op.execute("""
        UPDATE distribution 
        SET file_type = REPLACE(file_type, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE file_type LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Revert distribution_spatial_restrictions table
    op.execute("""
        UPDATE distribution_spatial_restrictions 
        SET key = REPLACE(key, 'http://publications.europa.eu/resource/authority/', 'https://publications.europa.eu/resource/authority/')
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # STEP 3: Delete old HTTP rows from lookup tables

    # Delete HTTP rows from theme table
    op.execute("""
        DELETE FROM theme 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTP rows from periodicity table
    op.execute("""
        DELETE FROM periodicity 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTP rows from file_type table
    op.execute("""
        DELETE FROM file_type 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTP rows from language table
    op.execute("""
        DELETE FROM language 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTP rows from dataset_type table
    op.execute("""
        DELETE FROM dataset_type 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)

    # Delete HTTP rows from spatial_coverage table
    op.execute("""
        DELETE FROM spatial_coverage 
        WHERE key LIKE 'http://publications.europa.eu/resource/authority/%'
        """)
