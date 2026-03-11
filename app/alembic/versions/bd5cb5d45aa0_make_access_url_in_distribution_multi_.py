"""make access url in distribution multi value

Revision ID: bd5cb5d45aa0
Revises: b7f436e5634a
Create Date: 2026-02-10 15:27:47.627324

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "bd5cb5d45aa0"
down_revision: Union[str, None] = "b7f436e5634a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_access_urls",
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
        INSERT INTO distribution_access_urls (distribution_id, url)
        SELECT id, access_url
        FROM distribution
        WHERE access_url IS NOT NULL AND access_url != ''
    """))

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("access_url")


def downgrade() -> None:
    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(sa.Column("access_url", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE distribution
        SET access_url = (
            SELECT url
            FROM distribution_access_urls
            WHERE distribution_access_urls.distribution_id = distribution.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT distribution_id FROM distribution_access_urls)
    """))

    op.drop_table("distribution_access_urls")
