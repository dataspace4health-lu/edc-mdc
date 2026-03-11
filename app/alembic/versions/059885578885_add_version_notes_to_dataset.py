"""add version notes to dataset

Revision ID: 059885578885
Revises: 68bce888fed1
Create Date: 2025-07-17 10:26:05.706716

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "059885578885"
down_revision: Union[str, None] = "68bce888fed1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_table("dataset_version_note")

    op.add_column("dataset", sa.Column("version_notes", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("dataset", "version_notes")

    op.create_table(
        "dataset_version_note",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.INTEGER(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String(), nullable=False),
    )
