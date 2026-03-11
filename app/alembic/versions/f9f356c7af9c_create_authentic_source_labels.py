"""create authentic source labels

Revision ID: f9f356c7af9c
Revises: aae119fb9eb0
Create Date: 2025-06-25 15:24:04.617685

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f9f356c7af9c"
down_revision: Union[str, None] = "aae119fb9eb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "authentic_source_label",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("user.id"), nullable=True),
        sa.UniqueConstraint("name", name="uq_authentic_source_label_name"),
    )

    op.create_table(
        "authentic_source_assignment",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "data_dictionary_entry_id",
            sa.Integer,
            sa.ForeignKey("data_dictionary_entry.id"),
            nullable=False,
        ),
        sa.Column(
            "authentic_source_label_id",
            sa.Integer,
            sa.ForeignKey("authentic_source_label.id"),
            nullable=False,
        ),
        sa.Column("assigned_by", sa.Integer, sa.ForeignKey("user.id"), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    )

    op.create_index(
        "ix_authentic_source_assignment_entry_id",
        "authentic_source_assignment",
        ["data_dictionary_entry_id"],
    )
    op.create_index(
        "ix_authentic_source_assignment_label_id",
        "authentic_source_assignment",
        ["authentic_source_label_id"],
    )
    op.create_index(
        "ix_authentic_source_assignment_is_active",
        "authentic_source_assignment",
        ["is_active"],
    )
    op.create_index(
        "ix_authentic_source_assignment_assigned_at",
        "authentic_source_assignment",
        ["assigned_at"],
    )


def downgrade() -> None:
    op.drop_table("authentic_source_assignment")
    op.drop_table("authentic_source_label")
