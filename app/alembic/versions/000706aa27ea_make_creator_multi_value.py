"""make creator multi-value

Revision ID: 000706aa27ea
Revises: c3833b13fb06
Create Date: 2026-01-20 14:27:21.663351

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "000706aa27ea"
down_revision: Union[str, None] = "c3833b13fb06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the junction table for dataset creators
    op.create_table(
        "dataset_creators",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("dataset.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisations.id"),
            nullable=False,
        ),
    )

    # Migrate existing creator_id data to the new junction table
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO dataset_creators (dataset_id, organisation_id)
        SELECT id, creator_id 
        FROM dataset 
        WHERE creator_id IS NOT NULL
    """))

    # Drop the old creator_id column and its foreign key
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_column("creator_id")


def downgrade() -> None:
    # Add back the creator_id column
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("creator_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_dataset_creator_id",
            "organisations",
            ["creator_id"],
            ["id"],
        )

    # Migrate data back (take the first creator from junction table)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE dataset
        SET creator_id = (
            SELECT organisation_id 
            FROM dataset_creators 
            WHERE dataset_creators.dataset_id = dataset.id 
            LIMIT 1
        )
        WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_creators)
    """))

    # Drop the junction table
    op.drop_table("dataset_creators")
