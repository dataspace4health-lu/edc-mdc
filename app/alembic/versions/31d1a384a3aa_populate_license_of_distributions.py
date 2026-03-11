"""populate license of distributions

Revision ID: 31d1a384a3aa
Revises: bc8711162df4
Create Date: 2024-09-16 19:59:26.966361

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "31d1a384a3aa"
down_revision: Union[str, None] = "bc8711162df4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.bulk_insert(
        sa.table(
            "license", sa.column("key", sa.String), sa.column("eng_label", sa.String)
        ),
        [
            {"key": "Apache-2.0", "eng_label": "Apache License 2.0"},
            {"key": "BSD-3-Clause", "eng_label": "BSD 3-Clause License"},
            {"key": "CC-BY-4.0", "eng_label": "Creative Commons Attribution 4.0"},
            {
                "key": "CC-BY-NC-4.0",
                "eng_label": "Creative Commons Attribution Non Commercial 4.0",
            },
            {
                "key": "CC-BY-ND-4.0",
                "eng_label": "Creative Commons Attribution No Derivatives 4.0",
            },
            {
                "key": "CC-BY-SA-4.0",
                "eng_label": "Creative Commons Attribution Share Alike 4.0",
            },
            {"key": "CC0-1.0", "eng_label": "Creative Commons Zero v1.0 Universal"},
            {"key": "GPL-3.0", "eng_label": "GNU General Public License v3.0"},
            {"key": "MIT", "eng_label": "MIT License"},
            {"key": "no_license", "eng_label": "No License"},
            {
                "key": "ODC-By-1.0",
                "eng_label": "Open Data Commons Attribution License v1.0",
            },
            {
                "key": "PDDL-1.0",
                "eng_label": "Open Data Commons Public Domain Dedication and License v1.0",
            },
            {"key": "ODbL-1.0", "eng_label": "Open Database License v1.0"},
            {"key": "other", "eng_label": "Other"},
        ],
    )


def downgrade():
    op.execute("DELETE FROM license")
