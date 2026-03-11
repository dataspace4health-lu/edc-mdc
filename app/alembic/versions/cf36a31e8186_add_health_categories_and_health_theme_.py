"""add health categories and health theme to dataset

Revision ID: cf36a31e8186
Revises: 7ac7d043807e
Create Date: 2025-12-18 12:42:29.801818

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cf36a31e8186"
down_revision: Union[str, None] = "7ac7d043807e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# to make it healthDCAT compliant we are adding these two new tables and the joint tables
def upgrade() -> None:
    op.create_table(
        "health_category",
        sa.Column("key", sa.String(length=100), primary_key=True, index=True),
        sa.Column("eng_label", sa.String(length=500)),
    )

    op.create_table(
        "health_theme",
        sa.Column("key", sa.String(length=100), primary_key=True, index=True),
        sa.Column("eng_label", sa.String(length=500)),
    )

    op.create_table(
        "dataset_health_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id", sa.Integer(), sa.ForeignKey("dataset.id"), nullable=False
        ),
        sa.Column(
            "key",
            sa.String(length=100),
            sa.ForeignKey("health_category.key"),
            nullable=False,
        ),
    )

    op.create_table(
        "dataset_health_themes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id", sa.Integer(), sa.ForeignKey("dataset.id"), nullable=False
        ),
        sa.Column(
            "key",
            sa.String(length=100),
            sa.ForeignKey("health_theme.key"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_health_themes")
    op.drop_table("dataset_health_categories")

    op.drop_table("health_theme")
    op.drop_table("health_category")
