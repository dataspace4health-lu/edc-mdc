"""convert conforms to to multi value

Revision ID: 0ea3e1d4f5f8
Revises: d6fd233d980e
Create Date: 2026-01-23 14:02:45.561232

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0ea3e1d4f5f8"
down_revision: Union[str, None] = "d6fd233d980e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_conforms_to",
        sa.Column(
            "id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True
        ),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset.id"],
        ),
    )
    op.create_index(
        op.f("ix_dataset_conforms_to_id"), "dataset_conforms_to", ["id"], unique=False
    )

    op.execute("""
        INSERT INTO dataset_conforms_to (dataset_id, key)
        SELECT id, conforms_to FROM dataset WHERE conforms_to IS NOT NULL AND conforms_to != ''
    """)

    op.drop_column("dataset", "conforms_to")


def downgrade() -> None:
    op.add_column("dataset", sa.Column("conforms_to", sa.String(), nullable=True))

    op.execute("""
        UPDATE dataset
        SET conforms_to = (
            SELECT key FROM dataset_conforms_to
            WHERE dataset_conforms_to.dataset_id = dataset.id
            LIMIT 1
        )
    """)

    op.drop_index(op.f("ix_dataset_conforms_to_id"), table_name="dataset_conforms_to")
    op.drop_table("dataset_conforms_to")
