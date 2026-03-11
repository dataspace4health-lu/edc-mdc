"""create distribution_languages table

Revision ID: b8a9b7140f28
Revises: cb3b2f00acab
Create Date: 2023-10-11 14:22:53.495465

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "b8a9b7140f28"
down_revision: Union[str, None] = "cb3b2f00acab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create a new table 'distribution_languages' for the many-to-many relationship
    op.create_table(
        "distribution_languages",
        sa.Column("id", sa.INTEGER(), primary_key=True, autoincrement=True, index=True),
        sa.Column("distribution_id", sa.INTEGER(), nullable=False),
        sa.Column("key", sa.VARCHAR(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["distribution_id"],
            ["distribution.id"],
        ),
        sa.ForeignKeyConstraint(
            ["key"],
            ["language.key"],
        ),
    )

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("language")


def downgrade() -> None:
    op.add_column(
        "distribution",
        sa.Column(
            "language",
            sa.VARCHAR(length=100),
            sa.ForeignKey("language.key"),
            nullable=True,
        ),
    )
    op.drop_table("distribution_languages")
