"""add status to dataset

Revision ID: 6cf1575b74e7
Revises: cac830252894
Create Date: 2024-05-28 11:05:30.221881

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6cf1575b74e7"
down_revision: Union[str, None] = "cac830252894"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "status",
        sa.Column("key", sa.VARCHAR(length=100), primary_key=True),
        sa.Column("eng_label", sa.VARCHAR(length=100), index=True),
    )

    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("status", sa.VARCHAR(length=100), nullable=True))
        batch_op.create_foreign_key("fk_status_key", "status", ["status"], ["key"])

    op.execute("""
        INSERT INTO status (key, eng_label) VALUES
            ('Internal only', 'Internal only'),
            ('Public catalogue', 'Public catalogue')
        """)


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("fk_status_key", type_="foreignkey")
        batch_op.drop_column("status")
    op.drop_table("status")
