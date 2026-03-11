"""convert single org form fields to multi-org form-fields

Revision ID: 95f0d89a28a9
Revises: 434c89264f4b
Create Date: 2025-08-14 11:56:21.855676

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "95f0d89a28a9"
down_revision: Union[str, None] = "434c89264f4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "keyword_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("keyword_key", sa.VARCHAR(length=100), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["keyword_key"], ["keyword.key"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["organisation_id"], ["organisations.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("keyword_key", "organisation_id"),
    )

    op.create_table(
        "legal_basis_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("legal_basis_key", sa.VARCHAR(length=100), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["legal_basis_key"], ["legal_basis.key"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["organisation_id"], ["organisations.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("legal_basis_key", "organisation_id"),
    )

    op.execute("""
        INSERT INTO keyword_assignments (keyword_key, organisation_id)
        SELECT key, organisation_id 
        FROM keyword 
        WHERE organisation_id IS NOT NULL
    """)

    op.execute("""
        INSERT INTO legal_basis_assignments (legal_basis_key, organisation_id)
        SELECT key, organisation_id
        FROM legal_basis
        WHERE organisation_id IS NOT NULL
    """)

    try:
        op.drop_index("ix_keyword_organisation_id", table_name="keyword")
    except:
        pass

    try:
        op.drop_index("ix_legal_basis_organisation_id", table_name="legal_basis")
    except:
        pass

    with op.batch_alter_table("keyword") as batch_op:
        batch_op.drop_column("organisation_id")

    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.drop_column("organisation_id")


def downgrade() -> None:
    with op.batch_alter_table("keyword") as batch_op:
        batch_op.add_column(sa.Column("organisation_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_keyword_organisation",
            "organisations",
            ["organisation_id"],
            ["id"],
            ondelete="SET NULL",
        )

    with op.batch_alter_table("legal_basis") as batch_op:
        batch_op.add_column(sa.Column("organisation_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_legal_basis_organisation_id_organisations",
            "organisations",
            ["organisation_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_index("ix_keyword_organisation_id", "keyword", ["organisation_id"])
    op.create_index(
        "ix_legal_basis_organisation_id", "legal_basis", ["organisation_id"]
    )

    op.execute("""
        UPDATE keyword 
        SET organisation_id = (
            SELECT organisation_id 
            FROM keyword_assignments 
            WHERE keyword_assignments.keyword_key = keyword.key 
            ORDER BY keyword_assignments.id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM keyword_assignments 
            WHERE keyword_assignments.keyword_key = keyword.key
        )
    """)

    op.execute("""
        UPDATE legal_basis 
        SET organisation_id = (
            SELECT organisation_id 
            FROM legal_basis_assignments 
            WHERE legal_basis_assignments.legal_basis_key = legal_basis.key 
            ORDER BY legal_basis_assignments.id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM legal_basis_assignments 
            WHERE legal_basis_assignments.legal_basis_key = legal_basis.key
        )
    """)

    op.drop_table("legal_basis_assignments")
    op.drop_table("keyword_assignments")
