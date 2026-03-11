"""convert dataset release_date from datetime to date

Revision ID: cfd71dad620c
Revises: 3d3559ffe62c
Create Date: 2025-08-12 13:37:05.909112

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "cfd71dad620c"
down_revision: Union[str, None] = "3d3559ffe62c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    convert_datetime_to_date("dataset", "release_date")


def downgrade() -> None:
    convert_date_to_datetime("dataset", "release_date")


def convert_datetime_to_date(table_name: str, column_name: str) -> None:
    # Add temporary column with date type
    op.add_column(table_name, sa.Column(f"{column_name}_date", sa.Date()))

    # Extract the date part from the datetime - works for both PostgreSQL and SQLite
    op.execute(
        text(
            f"UPDATE {table_name} SET {column_name}_date = DATE({column_name}) WHERE {column_name} IS NOT NULL"
        )
    )

    # Drop the original column and rename the new one
    op.drop_column(table_name, column_name)
    op.alter_column(table_name, f"{column_name}_date", new_column_name=column_name)


def convert_date_to_datetime(table_name: str, column_name: str) -> None:
    # Add temporary column with timezone-aware datetime type
    op.add_column(
        table_name, sa.Column(f"{column_name}_dt", sa.DateTime(timezone=True))
    )

    # Simply copy the date value to the datetime column
    op.execute(
        text(
            f"UPDATE {table_name} SET {column_name}_dt = {column_name} WHERE {column_name} IS NOT NULL"
        )
    )

    # Drop the original column and rename the new one
    op.drop_column(table_name, column_name)
    op.alter_column(table_name, f"{column_name}_dt", new_column_name=column_name)
