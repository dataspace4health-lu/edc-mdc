"""Add default no_license to existing distributions

Revision ID: 4cf90a6c0e02
Revises: 31d1a384a3aa
Create Date: 2024-09-23 10:57:06.325939

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import insert

# revision identifiers, used by Alembic.
revision: str = "4cf90a6c0e02"
down_revision: Union[str, None] = "31d1a384a3aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    connection = op.get_bind()

    distribution = table(
        "distribution", column("id", sa.Integer), column("license", sa.String)
    )

    license_table = table(
        "license", column("key", sa.String), column("eng_label", sa.String)
    )

    insert_stmt = insert(license_table).values(key="no_license", eng_label="No License")
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["key"])
    connection.execute(do_nothing_stmt)

    connection.execute(
        distribution.update()
        .where(distribution.c.license.is_(None))
        .values(license="no_license")
    )


def downgrade():
    connection = op.get_bind()

    distribution = table(
        "distribution", column("id", sa.Integer), column("license", sa.String)
    )

    license_table = table("license", column("key", sa.String))

    connection.execute(
        distribution.update()
        .where(distribution.c.license == "no_license")
        .values(license=None)
    )

    connection.execute(
        license_table.delete().where(license_table.c.key == "no_license")
    )
