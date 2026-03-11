"""Populate organisations from existing datasets

Revision ID: 94d65626afeb
Revises: 121fcc575247
Create Date: 2024-10-06 13:16:11.218427

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "94d65626afeb"
down_revision: Union[str, None] = "121fcc575247"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()

    datasets = connection.execute(text("""
        SELECT id, publisher_name, creator, contact_email
        FROM dataset
        WHERE publisher_name IS NOT NULL OR creator IS NOT NULL
    """)).fetchall()

    for dataset in datasets:
        publisher_name = dataset.publisher_name
        creator = dataset.creator
        contact_email = dataset.contact_email

        if publisher_name:
            orgs = connection.execute(
                text("""
                SELECT id
                FROM organisations
                WHERE name = :name
            """),
                {"name": publisher_name},
            ).fetchone()

            if not orgs:
                connection.execute(
                    text("""
                    INSERT INTO organisations (name, type, email)
                    VALUES (:name, 'national_authority', :email)
                    ON CONFLICT (id) DO NOTHING
                """),
                    {"name": publisher_name, "email": contact_email},
                )

        if creator:
            orgs = connection.execute(
                text("""
                SELECT id
                FROM organisations
                WHERE name = :name
            """),
                {"name": creator},
            ).fetchone()

            if not orgs:
                connection.execute(
                    text("""
                    INSERT INTO organisations (name, type, email)
                    VALUES (:name, 'national_authority', :email)
                    ON CONFLICT (id) DO NOTHING
                """),
                    {"name": creator, "email": contact_email},
                )


def downgrade():
    connection = op.get_bind()

    connection.execute(text("""
        DELETE FROM organisations
    """))
