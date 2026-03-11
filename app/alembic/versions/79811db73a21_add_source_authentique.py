"""Add source_authentique

Revision ID: 79811db73a21
Revises: b909662313cd
Create Date: 2025-04-14 15:38:38.104303

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "79811db73a21"
down_revision: Union[str, None] = "63be8bcc6d57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_dictionary_entry",
        sa.Column(
            "is_authentic_source",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "dataset",
        sa.Column(
            "is_dataset_authentic_source", sa.Boolean, nullable=True
        ),  # nullable indicates no override
    )


def downgrade() -> None:
    op.drop_column("data_dictionary_entry", "is_authentic_source")
    op.drop_column("dataset", "is_dataset_authentic_source")
