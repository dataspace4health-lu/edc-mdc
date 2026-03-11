"""Remove right_statements

Revision ID: 8d34466d194d
Revises: cbb6978e51d3
Create Date: 2025-03-17 10:55:48.409055

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision: str = "8d34466d194d"
down_revision: Union[str, None] = "cbb6978e51d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if is_dev_or_test_env():
        # There is no way to remove foreign key constraints in SQLite if it has no name.
        with op.batch_alter_table("dataset", schema=None) as batch_op:
            batch_op.drop_column("rights_statement")

        with op.batch_alter_table("dataset", schema=None) as batch_op:
            batch_op.add_column(sa.Column("rights_statement", sa.VARCHAR(length=100)))

        with op.batch_alter_table("distribution", schema=None) as batch_op:
            batch_op.drop_column("rights_statement")

        with op.batch_alter_table("distribution", schema=None) as batch_op:
            batch_op.add_column(sa.Column("rights_statement", sa.VARCHAR(length=100)))
    else:
        op.drop_constraint(
            "dataset_rights_statement_fkey", "dataset", type_="foreignkey"
        )
        op.drop_constraint(
            "fk_distribution_rights_statement", "distribution", type_="foreignkey"
        )
    op.drop_table("rights_statement")


def downgrade() -> None:
    pass


def is_dev_or_test_env() -> bool:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    return ENVIRONMENT == "development" or ENVIRONMENT == "test"
