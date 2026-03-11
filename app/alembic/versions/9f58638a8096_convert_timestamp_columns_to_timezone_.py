"""convert timestamp columns to timezone-aware

Revision ID: 9f58638a8096
Revises: 4f7d3c4bed7d
Create Date: 2025-05-16 13:46:12.273792

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import os

# revision identifiers, used by Alembic.
revision: str = "9f58638a8096"
down_revision: Union[str, None] = "4f7d3c4bed7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    db_timezone = os.environ.get("DB_TIMEZONE")

    migrate_to_timezone_aware_columns(
        "activity_log", "timestamp", db_timezone, needs_default=True
    )
    migrate_to_timezone_aware_columns(
        "dataset_comments", "timestamp", db_timezone, needs_default=True
    )
    migrate_to_timezone_aware_columns(
        "dataset", "submitted_at", db_timezone, needs_default=True
    )
    migrate_to_timezone_aware_columns(
        "dataset", "released_at", db_timezone, needs_default=False
    )
    migrate_to_timezone_aware_columns(
        "dataset", "modified_at", db_timezone, needs_default=False
    )
    migrate_to_timezone_aware_columns(
        "distribution", "modification_date", db_timezone, needs_default=False
    )
    migrate_to_timezone_aware_columns(
        "distribution", "release_date", db_timezone, needs_default=False
    )


def downgrade() -> None:
    pass


def migrate_to_timezone_aware_columns(
    table_name: str, column_name: str, db_timezone: str, needs_default: bool
) -> None:
    need_tz_conversion = db_timezone is not None and db_timezone != "UTC"

    op.add_column(
        table_name, sa.Column(f"{column_name}_tz", sa.DateTime(timezone=True))
    )

    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        # PostgreSQL-specific timezone handling
        if need_tz_conversion:
            # For PostgreSQL with non-UTC timezone
            conn.execute(
                text(
                    f"UPDATE {table_name} SET {column_name}_tz = {column_name} AT TIME ZONE '{db_timezone}' WHERE {column_name} IS NOT NULL"
                )
            )
        else:
            # For PostgreSQL with UTC timezone
            conn.execute(
                text(
                    f"UPDATE {table_name} SET {column_name}_tz = {column_name} AT TIME ZONE 'UTC' WHERE {column_name} IS NOT NULL"
                )
            )

        # Default for PostgreSQL
        if needs_default:
            default_expr = sa.text("(now() AT TIME ZONE 'UTC')")
    else:
        # SQLite or other databases
        # Simple copy without timezone conversion
        conn.execute(
            text(
                f"UPDATE {table_name} SET {column_name}_tz = {column_name} WHERE {column_name} IS NOT NULL"
            )
        )

        # Default for SQLite
        if needs_default:
            default_expr = sa.text("CURRENT_TIMESTAMP")

    # Drop old column and rename new one
    op.drop_column(table_name, column_name)
    op.alter_column(table_name, f"{column_name}_tz", new_column_name=column_name)

    # Apply default if needed
    if needs_default:
        if dialect == "postgresql":
            op.alter_column(
                table_name,
                column_name,
                server_default=default_expr,
            )
        else:
            # For SQLite, the default might need to be handled differently
            # depending on the SQLite version and SQLAlchemy version
            try:
                op.alter_column(
                    table_name,
                    column_name,
                    server_default=default_expr,
                )
            except Exception:
                # SQLite might not support changing defaults on existing columns
                # In that case, we'll skip setting the default in SQLite
                pass
