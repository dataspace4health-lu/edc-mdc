"""make activity_log user nullable set null on delete

Revision ID: b174c0b30651
Revises: b97268c73031
Create Date: 2026-02-11 15:59:05.920416

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b174c0b30651"
down_revision: Union[str, None] = "b97268c73031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name

    with op.batch_alter_table("activity_log", schema=None) as batch_op:
        # PostgreSQL has a stable default FK name here; in SQLite it's typically unnamed.
        if dialect == "postgresql":
            batch_op.drop_constraint("activity_log_user_id_fkey", type_="foreignkey")

        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=True)

        if dialect == "postgresql":
            batch_op.create_foreign_key(
                "activity_log_user_id_fkey",
                "user",
                ["user_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    dialect = op.get_bind().dialect.name

    # `SET NULL` in the upgraded FK can produce rows that violate the original
    # non-null constraint during downgrade. Remove them before restoring NOT NULL.
    op.execute(sa.text("DELETE FROM activity_log WHERE user_id IS NULL"))

    with op.batch_alter_table("activity_log", schema=None) as batch_op:
        if dialect == "postgresql":
            batch_op.drop_constraint("activity_log_user_id_fkey", type_="foreignkey")

        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)

        if dialect == "postgresql":
            batch_op.create_foreign_key(
                "activity_log_user_id_fkey",
                "user",
                ["user_id"],
                ["id"],
            )
