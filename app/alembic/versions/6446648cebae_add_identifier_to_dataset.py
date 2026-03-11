"""add UUID-like identifier to dataset

Revision ID: 6446648cebae
Revises: f32f99e75110
Create Date: 2024-08-30 09:46:03.589745

"""

from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = "6446648cebae"
down_revision = "f32f99e75110"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.add_column(sa.Column("identifier", sa.String(36), nullable=True))

    connection = op.get_bind()
    datasets = connection.execute(
        sa.text("SELECT id FROM dataset WHERE identifier IS NULL")
    ).fetchall()
    for dataset in datasets:
        new_identifier = str(uuid.uuid1())
        connection.execute(
            sa.text("UPDATE dataset SET identifier = :uuid WHERE id = :id"),
            {"uuid": new_identifier, "id": dataset[0]},
        )

    with op.batch_alter_table("dataset") as batch_op:
        batch_op.alter_column("identifier", nullable=False)
        batch_op.create_unique_constraint("uq_dataset_identifier", ["identifier"])


def downgrade():
    with op.batch_alter_table("dataset") as batch_op:
        batch_op.drop_constraint("uq_dataset_identifier", type_="unique")
        batch_op.drop_column("identifier")
