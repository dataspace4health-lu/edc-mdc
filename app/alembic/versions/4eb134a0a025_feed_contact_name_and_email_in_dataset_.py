"""feed contact_name and email in dataset from the contacts table

Revision ID: 4eb134a0a025
Revises: da98930f2e91
Create Date: 2024-10-17 15:23:51.525836

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4eb134a0a025"
down_revision: Union[str, None] = "7b7cbd1860ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("contact_id", sa.Integer(), nullable=True))

        batch_op.create_foreign_key(
            "fk_contact_id",
            "contacts",
            ["contact_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("fk_contact_id", type_="foreignkey")
        batch_op.drop_column("contact_id")
