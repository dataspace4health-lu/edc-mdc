"""convert single policy action to multi-policy actions

Revision ID: a47ea18b48e5
Revises: cb02aeec83fe
Create Date: 2025-09-10 15:09:19.851022
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a47ea18b48e5"
down_revision: Union[str, None] = "cb02aeec83fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "distribution_policy_actions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("distribution_id", sa.Integer(), nullable=False),
        sa.Column("policy_action_type", sa.String(length=50), nullable=False),
        sa.Column("policy_constraint_type", sa.String(length=50), nullable=True),
        sa.Column("policy_constraint_value", sa.String(length=255), nullable=True),
        sa.Column("temporal_restriction_start", sa.Date(), nullable=True),
        sa.Column("temporal_restriction_end", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["distribution_id"], ["distribution.id"], ondelete="CASCADE"
        ),
    )

    op.execute("""
        INSERT INTO distribution_policy_actions (distribution_id, policy_action_type, policy_constraint_type, policy_constraint_value, temporal_restriction_start, temporal_restriction_end)
        SELECT id, policy_action_type, policy_constraint_type, policy_constraint_value, temporal_restriction_start, temporal_restriction_end
        FROM distribution
        WHERE policy_action_type IS NOT NULL
        """)

    with op.batch_alter_table("distribution_spatial_restrictions") as batch_op:
        batch_op.add_column(sa.Column("policy_action_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_spatial_restrictions_policy_action",
            "distribution_policy_actions",
            ["policy_action_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.execute("""
        UPDATE distribution_spatial_restrictions
        SET policy_action_id = (
            SELECT dpa.id
            FROM distribution_policy_actions dpa
            WHERE dpa.distribution_id = distribution_spatial_restrictions.distribution_id
              AND dpa.policy_constraint_type = 'spatial'
            ORDER BY dpa.id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM distribution_policy_actions dpa
            WHERE dpa.distribution_id = distribution_spatial_restrictions.distribution_id
              AND dpa.policy_constraint_type = 'spatial'
        )
        """)

    op.execute("""
        INSERT INTO distribution_policy_actions (distribution_id, policy_action_type, policy_constraint_type)
        SELECT DISTINCT distribution_id, 'permission', 'spatial'
        FROM distribution_spatial_restrictions dsr
        WHERE policy_action_id IS NULL
          AND NOT EXISTS (
              SELECT 1 FROM distribution_policy_actions dpa
              WHERE dpa.distribution_id = dsr.distribution_id
                AND dpa.policy_constraint_type = 'spatial'
          )
        """)

    op.execute("""
        UPDATE distribution_spatial_restrictions
        SET policy_action_id = (
            SELECT dpa.id
            FROM distribution_policy_actions dpa
            WHERE dpa.distribution_id = distribution_spatial_restrictions.distribution_id
              AND dpa.policy_constraint_type = 'spatial'
            ORDER BY dpa.id DESC
            LIMIT 1
        )
        WHERE policy_action_id IS NULL
        """)

    with op.batch_alter_table("distribution_spatial_restrictions") as batch_op:
        batch_op.alter_column("policy_action_id", nullable=False)
        batch_op.drop_column("distribution_id")

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.drop_column("policy_action_type")
        batch_op.drop_column("policy_constraint_type")
        batch_op.drop_column("policy_constraint_value")
        batch_op.drop_column("temporal_restriction_start")
        batch_op.drop_column("temporal_restriction_end")


def downgrade() -> None:
    with op.batch_alter_table("distribution_spatial_restrictions") as batch_op:
        batch_op.add_column(sa.Column("distribution_id", sa.Integer(), nullable=True))

    op.execute("""
        UPDATE distribution_spatial_restrictions
        SET distribution_id = (
            SELECT distribution_id
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.id = distribution_spatial_restrictions.policy_action_id
        )
        """)

    with op.batch_alter_table("distribution") as batch_op:
        batch_op.add_column(
            sa.Column("policy_action_type", sa.String(50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("policy_constraint_type", sa.String(50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("policy_constraint_value", sa.String(255), nullable=True)
        )
        batch_op.add_column(
            sa.Column("temporal_restriction_start", sa.Date(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("temporal_restriction_end", sa.Date(), nullable=True)
        )

    op.execute("""
        UPDATE distribution
        SET policy_action_type = (
            SELECT policy_action_type
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
            ORDER BY distribution_policy_actions.id
            LIMIT 1
        ),
        policy_constraint_type = (
            SELECT policy_constraint_type
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
            ORDER BY distribution_policy_actions.id
            LIMIT 1
        ),
        policy_constraint_value = (
            SELECT policy_constraint_value
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
            ORDER BY distribution_policy_actions.id
            LIMIT 1
        ),
        temporal_restriction_start = (
            SELECT temporal_restriction_start
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
            ORDER BY distribution_policy_actions.id
            LIMIT 1
        ),
        temporal_restriction_end = (
            SELECT temporal_restriction_end
            FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
            ORDER BY distribution_policy_actions.id
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1 FROM distribution_policy_actions
            WHERE distribution_policy_actions.distribution_id = distribution.id
        )
        """)

    with op.batch_alter_table("distribution_spatial_restrictions") as batch_op:
        batch_op.drop_constraint(
            "fk_spatial_restrictions_policy_action", type_="foreignkey"
        )
        batch_op.drop_column("policy_action_id")
        batch_op.alter_column("distribution_id", nullable=False)
        batch_op.create_foreign_key(
            "distribution_spatial_restrictions_distribution_id_fkey",
            "distribution",
            ["distribution_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.drop_table("distribution_policy_actions")
