"""make entity_id in activity log accept string

Revision ID: 4f7d3c4bed7d
Revises: 6051ac6ce17b
Create Date: 2025-05-11 11:49:11.139127

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4f7d3c4bed7d"
down_revision: Union[str, None] = "6051ac6ce17b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("activity_log") as batch_op:
        batch_op.alter_column(
            "entity_id",
            existing_type=sa.Integer(),
            type_=sa.String(),
        )


def downgrade():
    with op.batch_alter_table("activity_log") as batch_op:
        batch_op.alter_column(
            "entity_id",
            existing_type=sa.String(),
            type_=sa.Integer(),
        )
