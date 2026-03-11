"""Create organisation and contact tables

Revision ID: 12f226499e6c
Revises: 4cf90a6c0e02
Create Date: 2024-09-24 19:24:46.230734

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "12f226499e6c"
down_revision: Union[str, None] = "16f0f02ee01b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisations.id"),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("contacts")
    op.drop_table("organisations")
