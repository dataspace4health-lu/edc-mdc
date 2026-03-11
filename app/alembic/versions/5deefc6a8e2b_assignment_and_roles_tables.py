"""assignment and roles tables

Revision ID: 5deefc6a8e2b
Revises: 2f5d541b7eca
Create Date: 2025-05-19 15:39:02.687069

"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy import Column, INTEGER, ForeignKey, String

# revision identifiers, used by Alembic.
revision: str = "5deefc6a8e2b"
down_revision: Union[str, None] = "2f5d541b7eca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_organisation_assignment",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "user_id",
            INTEGER(),
            ForeignKey("user.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "organisation_id",
            INTEGER(),
            ForeignKey("organisations.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    op.create_table(
        "role",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column("name", String, nullable=False),
    )

    op.create_table(
        "role_assignment",
        Column("id", INTEGER(), primary_key=True, autoincrement=True, index=True),
        Column(
            "user_organisation_assignment_id",
            INTEGER(),
            ForeignKey("user_organisation_assignment.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "role_id",
            INTEGER(),
            ForeignKey("role.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("role_assignment")
    op.drop_table("role")
    op.drop_table("user_organisation_assignment")
