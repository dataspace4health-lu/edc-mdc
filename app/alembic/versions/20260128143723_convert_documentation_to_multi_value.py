"""convert documentation to multi-value

Revision ID: 20260128143723
Revises: 3e1546a4426c
Create Date: 2026-01-28 14:37:23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260128143723"
down_revision: Union[str, None] = "3e1546a4426c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_documentation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
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
        INSERT INTO dataset_documentation (dataset_id, value)
        SELECT id, documentation
        FROM dataset
        WHERE documentation IS NOT NULL AND documentation != ''
    """))

    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("documentation")


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("documentation", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE dataset
        SET documentation = (
            SELECT value
            FROM dataset_documentation
            WHERE dataset_documentation.dataset_id = dataset.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_documentation)
    """))

    op.drop_table("dataset_documentation")
