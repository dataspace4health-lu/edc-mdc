"""create confroms_to and linked_schemas

Revision ID: a80a05cee846
Revises: 79811e66292462a11db73a21
Create Date: 2025-04-15 11:44:18.620066

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy import Column, INTEGER, ForeignKey, String

# revision identifiers, used by Alembic.
revision: str = "a80a05cee846"
down_revision: Union[str, None] = "e66292462a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_conforms",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "dataset_id",
            INTEGER(),
            ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "key",
            String(),
            nullable=False,
        ),
    )

    op.create_table(
        "distribution_linked_schema",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "distribution_id",
            INTEGER(),
            ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "key",
            String(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("distribution_linked_schema")
    op.drop_table("dataset_conforms")
