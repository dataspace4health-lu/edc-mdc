"""convert contact point to multi select

Revision ID: 08254628a7ec
Revises: 000706aa27ea
Create Date: 2026-01-22 13:25:05.878583

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "08254628a7ec"
down_revision: Union[str, None] = "000706aa27ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_contacts",
        sa.Column(
            "id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True
        ),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], ondelete="CASCADE"),
    )

    op.create_index(
        "ix_dataset_contacts_dataset_id",
        "dataset_contacts",
        ["dataset_id"],
    )

    op.create_index(
        "ix_dataset_contacts_contact_id",
        "dataset_contacts",
        ["contact_id"],
    )

    op.execute("""
        INSERT INTO dataset_contacts (dataset_id, contact_id)
        SELECT id, contact_id
        FROM dataset
        WHERE contact_id IS NOT NULL
    """)

    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("contact_id")


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("contact_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "dataset_contact_id_fkey", "contacts", ["contact_id"], ["id"]
        )

    op.execute("""
        UPDATE dataset
        SET contact_id = (
            SELECT contact_id
            FROM dataset_contacts
            WHERE dataset_contacts.dataset_id = dataset.id
            LIMIT 1
        )
    """)

    op.drop_index("ix_dataset_contacts_contact_id", table_name="dataset_contacts")
    op.drop_index("ix_dataset_contacts_dataset_id", table_name="dataset_contacts")
    op.drop_table("dataset_contacts")
