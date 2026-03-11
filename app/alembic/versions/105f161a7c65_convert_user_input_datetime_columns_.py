"""convert user input datetime columns into date

Revision ID: 105f161a7c65
Revises: 9f58638a8096
Create Date: 2025-05-19 16:06:11.063271

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "105f161a7c65"
down_revision: Union[str, None] = "9f58638a8096"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    convert_datetime_to_date("dataset", "modified_at")
    convert_datetime_to_date("distribution", "modification_date")
    convert_datetime_to_date("distribution", "release_date")


def downgrade() -> None:
    convert_date_to_datetime("dataset", "modified_at")
    convert_date_to_datetime("distribution", "modification_date")
    convert_date_to_datetime("distribution", "release_date")


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

    # Simply copy the date value to the datetime column - timezone will be handled by SQLAlchemy
    op.execute(
        text(
            f"UPDATE {table_name} SET {column_name}_dt = {column_name} WHERE {column_name} IS NOT NULL"
        )
    )

    # Drop the original column and rename the new one
    op.drop_column(table_name, column_name)
    op.alter_column(table_name, f"{column_name}_dt", new_column_name=column_name)
