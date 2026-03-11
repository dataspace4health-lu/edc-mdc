"""convert distribution documentation to multi-value

Revision ID: 20260212000000
Revises: b174c0b30651
Create Date: 2026-02-12 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260212000000"
down_revision: Union[str, None] = "b174c0b30651"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_documentation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("distribution.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.String(),
            nullable=False,
        ),
    )

    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO distribution_documentation (distribution_id, value)
        SELECT id, documentation
        FROM distribution
        WHERE documentation IS NOT NULL AND documentation != ''
    """))

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("documentation")


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(sa.Column("documentation", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE distribution
        SET documentation = (
            SELECT value
            FROM distribution_documentation
            WHERE distribution_documentation.distribution_id = distribution.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT distribution_id FROM distribution_documentation)
    """))

    op.drop_table("distribution_documentation")
