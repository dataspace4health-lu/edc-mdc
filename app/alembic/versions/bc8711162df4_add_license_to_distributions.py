"""add license to distributions

Revision ID: bc8711162df4
Revises: ea24e507533e
Create Date: 2024-09-16 19:40:58.132642

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bc8711162df4"
down_revision: Union[str, None] = "ea24e507533e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "license",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("eng_label", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_index(op.f("ix_license_key"), "license", ["key"], unique=False)

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(sa.Column("license", sa.String(), nullable=True))
        batch_op.create_foreign_key(
            "fk_distribution_license",
            "license",
            ["license"],
            ["key"],
        )


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_constraint("fk_distribution_license", type_="foreignkey")
        batch_op.drop_column("license")

    op.drop_index(op.f("ix_license_key"), table_name="license")
    op.drop_table("license")
