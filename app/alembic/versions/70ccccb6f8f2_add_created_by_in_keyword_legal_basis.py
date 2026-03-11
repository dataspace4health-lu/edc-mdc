"""add created_by in keyword, legal-basis

Revision ID: 70ccccb6f8f2
Revises: 97a5818bd3f7
Create Date: 2025-05-13 16:24:31.234607

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "70ccccb6f8f2"
down_revision: Union[str, None] = "97a5818bd3f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("keyword") as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_by_id",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_keyword_created_by_id_user", "user", ["created_by_id"], ["id"]
        )

    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_by_id",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_legal_basis_created_by_id_user", "user", ["created_by_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("keyword") as batch_op:
        batch_op.drop_column("created_by_id")
    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.drop_column("created_by_id")
