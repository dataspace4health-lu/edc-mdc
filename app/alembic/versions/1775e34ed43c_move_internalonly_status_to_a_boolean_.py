"""Move internalOnly status to a boolean flag

Revision ID: 1775e34ed43c
Revises: 12f226499e6c
Create Date: 2024-10-03 10:20:56.398186

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1775e34ed43c"
down_revision: Union[str, None] = "12f226499e6c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("internal_only", sa.Boolean, default=False))
        batch_op.drop_constraint("fk_status_key", type_="foreignkey")

    op.drop_table("status")
    op.execute("""
        UPDATE dataset
        SET internal_only = CASE
            WHEN status = 'Internal only' THEN TRUE
            ELSE FALSE
        END
    """)

    op.execute("""
        UPDATE dataset
        SET status = 'DRAFT'
    """)


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("internal_only")
        batch_op.create_foreign_key("fk_status_key", "status", ["status"], ["key"])

    op.create_table(
        "status",
        sa.Column("key", sa.VARCHAR(length=100), primary_key=True),
        sa.Column("eng_label", sa.VARCHAR(length=100), index=True),
    )

    op.execute("""
        INSERT INTO status (key, eng_label) VALUES
            ('Internal only', 'Internal only'),
            ('Public catalogue', 'Public catalogue')
        """)
