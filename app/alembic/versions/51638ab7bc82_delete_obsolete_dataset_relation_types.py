"""delete obsolete dataset relation types

Revision ID: 51638ab7bc82
Revises: d2e2b77ef800
Create Date: 2025-10-06 15:35:39.629016

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "51638ab7bc82"
down_revision: Union[str, None] = "d2e2b77ef800"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM dataset_relation 
        WHERE relation_type IN (
            'dct:conformsTo',
            'dct:hasFormat',
            'dct:isFormatOf',
            'dct:isRequiredBy',
            'dct:requires'
        )
        AND target_dataset IS NOT NULL
        """)


def downgrade() -> None:
    pass
