"""add labels to enum tables

Revision ID: 62acf83e5a26
Revises: 32760ddf7aee
Create Date: 2024-02-26 08:43:20.314141

"""

from typing import Sequence, Union
from sqlalchemy import Column, VARCHAR
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "62acf83e5a26"
down_revision: Union[str, None] = "32760ddf7aee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dataset_type", Column("eng_label", VARCHAR(length=100)))
    op.add_column("rights_statement", Column("eng_label", VARCHAR(length=100)))
    op.add_column("periodicity", Column("eng_label", VARCHAR(length=100)))
    op.add_column("theme", Column("eng_label", VARCHAR(length=100)))
    op.add_column("file_type", Column("eng_label", VARCHAR(length=100)))
    op.add_column("language", Column("eng_label", VARCHAR(length=100)))
    op.add_column("keyword", Column("eng_label", VARCHAR(length=100)))


def downgrade() -> None:
    op.drop_column("dataset_type", "eng_label")
    op.drop_column("rights_statement", "eng_label")
    op.drop_column("periodicity", "eng_label")
    op.drop_column("theme", "eng_label")
    op.drop_column("file_type", "eng_label")
    op.drop_column("language", "eng_label")
    op.drop_column("keyword", "eng_label")
