"""move records to accord de principe

Revision ID: aae119fb9eb0
Revises: 901b642a1c5a
Create Date: 2025-06-12 09:34:32.241835

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision: str = "aae119fb9eb0"
down_revision: Union[str, None] = "901b642a1c5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define table structures for the migration
    legal_basis = table(
        "legal_basis",
        column("key", sa.String),
        column("eng_label", sa.String),
        column("description", sa.String),
        column("link", sa.String),
        column("created_by_id", sa.Integer),
    )

    accord_de_principe = table(
        "accord_de_principe",
        column("key", sa.String),
        column("eng_label", sa.String),
        column("description", sa.String),
        column("link", sa.String),
        column("created_by_id", sa.Integer),
    )

    # Get connection
    connection = op.get_bind()

    # Define the keys to migrate
    keys_to_migrate = ["PL 8395 ARDNP", "PL 8395 ARDP", "PL 8395 TUDP"]

    # Fetch records from legal_basis
    result = connection.execute(
        sa.select(
            legal_basis.c.key,
            legal_basis.c.eng_label,
            legal_basis.c.description,
            legal_basis.c.link,
            legal_basis.c.created_by_id,
        ).where(legal_basis.c.key.in_(keys_to_migrate))
    )

    records_to_migrate = result.fetchall()

    # Insert records into accord_de_principe
    if records_to_migrate:
        for record in records_to_migrate:
            connection.execute(
                accord_de_principe.insert().values(
                    key=record.key,
                    eng_label=record.eng_label,
                    description=record.description,
                    link=record.link,
                    created_by_id=record.created_by_id,
                )
            )

    # Delete records from legal_basis
    connection.execute(
        legal_basis.delete().where(legal_basis.c.key.in_(keys_to_migrate))
    )


def downgrade() -> None:
    # Define table structures for the downgrade
    legal_basis = table(
        "legal_basis",
        column("key", sa.String),
        column("eng_label", sa.String),
        column("description", sa.String),
        column("link", sa.String),
        column("created_by_id", sa.Integer),
        column("organisation_id", sa.Integer),
    )

    accord_de_principe = table(
        "accord_de_principe",
        column("key", sa.String),
        column("eng_label", sa.String),
        column("description", sa.String),
        column("link", sa.String),
        column("created_by_id", sa.Integer),
    )

    # Get connection
    connection = op.get_bind()

    # Define the keys to move back
    keys_to_migrate = ["PL 8395 ARDNP", "PL 8395 ARDP", "PL 8395 TUDP"]

    # Fetch records from accord_de_principe
    result = connection.execute(
        sa.select(
            accord_de_principe.c.key,
            accord_de_principe.c.eng_label,
            accord_de_principe.c.description,
            accord_de_principe.c.link,
            accord_de_principe.c.created_by_id,
        ).where(accord_de_principe.c.key.in_(keys_to_migrate))
    )

    records_to_move_back = result.fetchall()

    # Insert records back into legal_basis
    if records_to_move_back:
        for record in records_to_move_back:
            connection.execute(
                legal_basis.insert().values(
                    key=record.key,
                    eng_label=record.eng_label,
                    description=record.description,
                    link=record.link,
                    created_by_id=record.created_by_id,
                    organisation_id=None,  # Setting to None since accord_de_principe doesn't have this field
                )
            )

    # Delete records from accord_de_principe
    connection.execute(
        accord_de_principe.delete().where(accord_de_principe.c.key.in_(keys_to_migrate))
    )
