"""make code values multi value

Revision ID: 6391a2b4a895
Revises: 4919d284c4ae
Create Date: 2026-02-20 11:48:52.708381

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6391a2b4a895"
down_revision: Union[str, None] = "4919d284c4ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if not inspector.has_table("dataset_code_values"):
        op.create_table(
            "dataset_code_values",
            sa.Column(
                "id", sa.Integer(), primary_key=True, autoincrement=True, index=True
            ),
            sa.Column("dataset_id", sa.Integer(), nullable=False),
            sa.Column("value", sa.String(), nullable=False),
            sa.ForeignKeyConstraint(["dataset_id"], ["dataset.id"], ondelete="CASCADE"),
        )

    dataset_columns = {column["name"] for column in inspector.get_columns("dataset")}
    if "has_code_values" in dataset_columns:
        connection.execute(sa.text("""
                INSERT INTO dataset_code_values (dataset_id, value)
                SELECT id, has_code_values
                FROM dataset
                WHERE has_code_values IS NOT NULL AND has_code_values != ''
                """))

        with op.batch_alter_table("dataset") as batch_op:
            batch_op.drop_column("has_code_values")


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    dataset_columns = {column["name"] for column in inspector.get_columns("dataset")}

    if "has_code_values" not in dataset_columns:
        with op.batch_alter_table("dataset") as batch_op:
            batch_op.add_column(
                sa.Column("has_code_values", sa.String(), nullable=True)
            )

    if inspector.has_table("dataset_code_values"):
        connection.execute(sa.text("""
                UPDATE dataset
                SET has_code_values = (
                    SELECT value
                    FROM dataset_code_values
                    WHERE dataset_code_values.dataset_id = dataset.id
                    ORDER BY dataset_code_values.id
                    LIMIT 1
                )
                WHERE id IN (SELECT DISTINCT dataset_id FROM dataset_code_values)
                """))
        op.drop_table("dataset_code_values")
