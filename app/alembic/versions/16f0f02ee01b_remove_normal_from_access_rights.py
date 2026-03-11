"""remove normal from access rights

Revision ID: 16f0f02ee01b
Revises: 7c3b7d76011c
Create Date: 2024-09-27 15:19:02.255639

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "16f0f02ee01b"
down_revision: Union[str, None] = "7c3b7d76011c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute(
        text(
            "DELETE FROM rights_statement WHERE key = 'https://publications.europa.eu/resource/authority/access-right/NORMAL'"
        )
    )

    op.execute(
        text(
            "UPDATE dataset SET rights_statement = 'https://publications.europa.eu/resource/authority/access-right/PUBLIC' WHERE rights_statement = 'https://publications.europa.eu/resource/authority/access-right/NORMAL'"
        )
    )

    op.execute(
        text(
            "UPDATE distribution SET rights_statement = 'https://publications.europa.eu/resource/authority/access-right/PUBLIC' WHERE rights_statement = 'https://publications.europa.eu/resource/authority/access-right/NORMAL'"
        )
    )


def downgrade() -> None:

    op.execute(
        text(
            "INSERT INTO rights_statement (key, eng_label) VALUES ('https://publications.europa.eu/resource/authority/access-right/NORMAL', 'normal')"
        )
    )

    op.execute(
        text(
            "UPDATE dataset SET rights_statement = 'https://publications.europa.eu/resource/authority/access-right/NORMAL' WHERE rights_statement = 'https://publications.europa.eu/resource/authority/access-right/PUBLIC'"
        )
    )

    op.execute(
        text(
            "UPDATE distribution SET rights_statement = 'https://publications.europa.eu/resource/authority/access-right/NORMAL' WHERE rights_statement = 'https://publications.europa.eu/resource/authority/access-right/PUBLIC'"
        )
    )
