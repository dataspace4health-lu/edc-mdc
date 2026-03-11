"""replace dataset_conforms table with single conforms_to

Revision ID: 2b5bac03003e
Revises: a407fd1cef5c
Create Date: 2025-07-22 14:30:50.889227

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b5bac03003e"
down_revision: Union[str, None] = "c37cd5065667"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("dataset_conforms")

    op.add_column(
        "dataset",
        sa.Column(
            "conforms_to",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("dataset", "conforms_to")

    op.create_table(
        "dataset_conforms",
        sa.Column("id", sa.INTEGER, primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.INTEGER,
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key", sa.String, nullable=False),
    )
