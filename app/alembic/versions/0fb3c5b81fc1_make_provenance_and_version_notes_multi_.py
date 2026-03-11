"""make provenance and version notes multi value

Revision ID: 0fb3c5b81fc1
Revises: 20260128143723
Create Date: 2026-01-30 12:22:32.516391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0fb3c5b81fc1"
down_revision: Union[str, None] = "a6e802a257a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_provenance_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Text(),
            nullable=False,
        ),
    )

    op.create_table(
        "dataset_version_notes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Text(),
            nullable=False,
        ),
    )

    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO dataset_provenance_entries (dataset_id, value)
        SELECT id, provenance
        FROM dataset
        WHERE provenance IS NOT NULL AND provenance != ''
    """))

    connection.execute(sa.text("""
        INSERT INTO dataset_version_notes (dataset_id, value)
        SELECT id, version_notes
        FROM dataset
        WHERE version_notes IS NOT NULL AND version_notes != ''
    """))

    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("provenance")
        batch_op.drop_column("version_notes")


def downgrade() -> None:
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("provenance", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("version_notes", sa.String(), nullable=True))

    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE dataset
        SET provenance = (
            SELECT value
            FROM dataset_provenance_entries
            WHERE dataset_provenance_entries.dataset_id = dataset.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_provenance_entries)
    """))

    connection.execute(sa.text("""
        UPDATE dataset
        SET version_notes = (
            SELECT value
            FROM dataset_version_notes
            WHERE dataset_version_notes.dataset_id = dataset.id
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_version_notes)
    """))

    op.drop_table("dataset_provenance_entries")
    op.drop_table("dataset_version_notes")
