"""fix policy action data migration issues

Revision ID: 097e27d6bba3
Revises: a47ea18b48e5
Create Date: 2025-09-23 12:01:53.153221

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "097e27d6bba3"
down_revision: Union[str, None] = "a47ea18b48e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE distribution_policy_actions
        SET policy_action_type = CASE
            WHEN LOWER(TRIM(policy_action_type)) LIKE '%permission%' THEN 'permission'
            WHEN LOWER(TRIM(policy_action_type)) LIKE '%prohibition%' THEN 'prohibition'
            WHEN LOWER(TRIM(policy_action_type)) LIKE '%allow%' THEN 'permission'
            WHEN LOWER(TRIM(policy_action_type)) LIKE '%deny%' THEN 'prohibition'
            WHEN LOWER(TRIM(policy_action_type)) LIKE '%forbid%' THEN 'prohibition'
            ELSE LOWER(TRIM(policy_action_type))
        END
        WHERE policy_action_type IS NOT NULL;
        """)

    op.execute("""
        UPDATE distribution_policy_actions
        SET policy_constraint_type = CASE
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%spatial%' THEN 'spatial'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%location%' THEN 'spatial'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%geo%' THEN 'spatial'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%temporal%' THEN 'temporal'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%time%' THEN 'temporal'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%date%' THEN 'temporal'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%purpose%' THEN 'purpose'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%industry%' THEN 'industry'
            WHEN LOWER(TRIM(policy_constraint_type)) LIKE '%sector%' THEN 'industry'
            ELSE LOWER(TRIM(policy_constraint_type))
        END
        WHERE policy_constraint_type IS NOT NULL;
        """)

    op.execute("""
        WITH ranked AS (
            SELECT 
                id,
                distribution_id,
                ROW_NUMBER() OVER (
                    PARTITION BY distribution_id
                    ORDER BY
                        -- Prioritize policy actions with actual spatial restrictions
                        CASE WHEN EXISTS (
                            SELECT 1 FROM distribution_spatial_restrictions dsr
                            WHERE dsr.policy_action_id = distribution_policy_actions.id
                        ) THEN 0 ELSE 1 END,
                        -- Then prioritize those with constraint values or temporal data
                        CASE WHEN policy_constraint_value IS NOT NULL 
                             OR temporal_restriction_start IS NOT NULL 
                             OR temporal_restriction_end IS NOT NULL 
                        THEN 0 ELSE 1 END,
                        -- Keep the oldest one
                        id ASC
                ) as rn
            FROM distribution_policy_actions
        )
        DELETE FROM distribution_policy_actions
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """)


def downgrade() -> None:
    pass
