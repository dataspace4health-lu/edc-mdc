"""populate contacts from dataset contacts

Revision ID: da98930f2e91
Revises: 372ab165f8dc
Create Date: 2024-10-17 14:53:17.407879

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "da98930f2e91"
down_revision: Union[str, None] = "4eb134a0a025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()

    insert_contacts = sa.text("""
        INSERT INTO contacts (name, email, organisation_id)
        SELECT DISTINCT contact_name AS name, contact_email AS email, publisher_id AS organisation_id
        FROM dataset
        WHERE contact_name IS NOT NULL AND contact_email IS NOT NULL AND publisher_id IS NOT NULL;
        """)
    connection.execute(insert_contacts)

    update_datasets = sa.text("""
        UPDATE dataset 
        SET contact_id = (
            SELECT id FROM contacts 
            WHERE organisation_id = dataset.publisher_id 
            AND email = dataset.contact_email 
            AND name = dataset.contact_name
        )
        """)
    connection.execute(update_datasets)

    op.drop_column("dataset", "contact_name")
    op.drop_column("dataset", "contact_email")


def downgrade() -> None:
    connection = op.get_bind()

    op.add_column("dataset", sa.Column("contact_name", sa.String(), nullable=True))
    op.add_column("dataset", sa.Column("contact_email"), sa.String(), nullable=True)

    connection.execute(sa.text("""
            UPDATE dataset
            SET contact_name = (SELECT name FROM contacts WHERE contacts.id = dataset.contact_id),
                contact_email = (SELECT email FROM contacts WHERE contacts.id = dataset.contact_id)
            WHERE contact_id IS NOT NULL;
            """))

    connection.execute(sa.text("""
            UPDATE dataset
            SET contact_id = NULL
            WHERE contact_id IN (
                SELECT id FROM contacts
            );
            """))

    connection.execute(sa.text("""
            DELETE FROM contacts 
            WHERE (name, email, organisation_id) IN (
                SELECT contact_name, contact_email, publisher_id 
                FROM dataset 
                WHERE contact_name IS NOT NULL AND contact_email IS NOT NULL AND publisher_id IS NOT NULL
            );
            """))
