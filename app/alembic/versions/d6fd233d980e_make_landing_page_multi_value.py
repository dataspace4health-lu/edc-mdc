"""make landing page multi-value

Revision ID: d6fd233d980e
Revises: 08254628a7ec
Create Date: 2026-01-22 15:55:17.156656

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d6fd233d980e"
down_revision: Union[str, None] = "08254628a7ec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the junction table for dataset landing pages
    op.create_table(
        "dataset_landing_pages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "url",
            sa.String(),
            nullable=False,
        ),
    )

    # Migrate existing landing_page data to the new junction table
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO dataset_landing_pages (dataset_id, url)
        SELECT id, landing_page
        FROM dataset
        WHERE landing_page IS NOT NULL AND landing_page != ''
    """))

    # Drop the old landing_page column
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("landing_page")


def downgrade() -> None:
    # Add back the landing_page column
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("landing_page", sa.String(), nullable=True))

    # Migrate data back (take the first landing page from junction table)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE dataset
        SET landing_page = (
            SELECT url
            FROM dataset_landing_pages
            WHERE dataset_landing_pages.dataset_id = dataset.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_landing_pages)
    """))

    # Drop the junction table
    op.drop_table("dataset_landing_pages")
