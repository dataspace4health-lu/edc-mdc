"""add rights statement to distributions

Revision ID: 3bbc159d3691
Revises: 75ca6d4a84dc
Create Date: 2024-05-15 15:46:12.285738

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR

# revision identifiers, used by Alembic.
revision: str = "3bbc159d3691"
down_revision: Union[str, None] = "75ca6d4a84dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(Column("rights_statement", VARCHAR(length=100)))
        batch_op.create_foreign_key(
            "fk_distribution_rights_statement",
            "rights_statement",
            ["rights_statement"],
            ["key"],
        )
    op.execute(
        "UPDATE distribution SET rights_statement = (SELECT dataset.rights_statement FROM dataset WHERE dataset.id = distribution.dataset_id)"
    )


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_constraint("fk_distribution_rights_statement", type_="foreignkey")
        batch_op.drop_column("rights_statement")
