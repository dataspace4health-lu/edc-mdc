"""make download url in distribution multi value

Revision ID: b97268c73031
Revises: bd5cb5d45aa0
Create Date: 2026-02-12 12:22:49.965942

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b97268c73031"
down_revision: Union[str, None] = "bd5cb5d45aa0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_download_urls",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "distribution_id",
            sa.Integer(),
            sa.ForeignKey("distribution.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "url",
            sa.String(),
            nullable=False,
        ),
    )

    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO distribution_download_urls (distribution_id, url)
        SELECT id, download_url
        FROM distribution
        WHERE download_url IS NOT NULL AND download_url != ''
    """))

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("download_url")


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(sa.Column("download_url", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE distribution
        SET download_url = (
            SELECT url
            FROM distribution_download_urls
            WHERE distribution_download_urls.distribution_id = distribution.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT distribution_id FROM distribution_download_urls)
    """))

    op.drop_table("distribution_download_urls")
