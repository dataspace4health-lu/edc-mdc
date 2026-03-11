"""remove publisher_name creator from dataset

Revision ID: a760cfd55499
Revises: 94d65626afeb
Create Date: 2024-10-06 18:44:17.832993

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "a760cfd55499"
down_revision: Union[str, None] = "94d65626afeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(text("""
            UPDATE dataset
            SET publisher_id = (
                SELECT id FROM organisations 
                WHERE organisations.name = dataset.publisher_name
            ),
            creator_id = (
                SELECT id FROM organisations 
                WHERE organisations.name = dataset.creator
            )
            WHERE publisher_name IS NOT NULL OR creator IS NOT NULL;
            """))

    op.drop_column("dataset", "publisher_name")
    op.drop_column("dataset", "creator")


def downgrade() -> None:
    op.add_column(
        "dataset", sa.Column("publisher_name", sa.String(length=100), nullable=True)
    )
    op.add_column("dataset", sa.Column("creator", sa.String(length=100), nullable=True))
