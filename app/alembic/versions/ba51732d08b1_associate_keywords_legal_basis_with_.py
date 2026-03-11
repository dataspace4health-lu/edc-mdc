"""associate keywords & legal basis with organisation

Revision ID: ba51732d08b1
Revises: 5deefc6a8e2b
Create Date: 2025-05-20 10:32:37.716347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ba51732d08b1"
down_revision: Union[str, None] = "5deefc6a8e2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("keyword") as batch_op:
        batch_op.add_column(sa.Column("organisation_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_keyword_organisation",
            "organisations",
            ["organisation_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index(
        "ix_keyword_organisation_id",
        "keyword",
        ["organisation_id"],
    )

    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.add_column(
            sa.Column(
                "organisation_id",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "fk_legal_basis_organisation_id_organisations",
            "organisations",
            ["organisation_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index(
        "ix_legal_basis_organisation_id", "legal_basis", ["organisation_id"]
    )


def downgrade() -> None:
    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.drop_constraint(
            "fk_legal_basis_organisation_id_organisations", type_="foreignkey"
        )
        batch_op.drop_column("organisation_id")
    op.drop_index("ix_legal_basis_organisation_id", table_name="legal_basis")

    with op.batch_alter_table("keyword") as batch_op:
        batch_op.drop_constraint(
            "fk_keyword_organisation_id_organisations", type_="foreignkey"
        )
        batch_op.drop_column("organisation_id")
    op.drop_index("ix_keyword_organisation_id", table_name="keyword")
