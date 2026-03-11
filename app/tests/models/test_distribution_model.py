from datetime import date
import pytest
from sqlalchemy.orm import Session
from models.distribution import (
    Distribution,
    DistributionLanguage,
    DistributionPolicyAction,
)
from models.dataset import Dataset
from dependencies.database import SessionLocal
from test_factory import sample_dataset


def test_distribution_languages(db_session: Session, sample_dataset: Dataset):
    db_session.add(sample_dataset)
    db_session.flush()

    distribution = list(sample_dataset.distributions)[0]

    dist_lang1 = DistributionLanguage(distribution_id=distribution.id, key="ENGLISH")
    dist_lang2 = DistributionLanguage(distribution_id=distribution.id, key="FRENCH")

    db_session.add(dist_lang1)
    db_session.add(dist_lang2)
    db_session.commit()

    db_dist = (
        db_session.query(Distribution).filter(Distribution.id == distribution.id).one()
    )

    language_keys = {lang.key for lang in db_dist.languages}
    assert "ENGLISH" in language_keys, "ENGLISH not found in distribution languages"
    assert "FRENCH" in language_keys, "FRENCH not found in distribution languages"


def test_distribution_policy_actions(db_session, sample_dataset):
    db_session.add(sample_dataset)
    db_session.commit()

    distribution = list(sample_dataset.distributions)[0]

    baseline = len(distribution.policy_actions)

    policy_action1 = DistributionPolicyAction(
        distribution_id=distribution.id,
        policy_action_type="permission",
        policy_constraint_type="purpose",
        policy_constraint_value="DUO:0000006",
    )

    policy_action2 = DistributionPolicyAction(
        distribution_id=distribution.id,
        policy_action_type="prohibition",
        policy_constraint_type="temporal",
        temporal_restriction_start=date(2024, 1, 1),
        temporal_restriction_end=date(2024, 12, 31),
    )

    policy_action3 = DistributionPolicyAction(
        distribution_id=distribution.id,
        policy_action_type="permission",
        policy_constraint_type="spatial",
    )

    db_session.add_all([policy_action1, policy_action2, policy_action3])
    db_session.commit()

    db_dist = db_session.query(Distribution).filter_by(id=distribution.id).one()

    actions = list(db_dist.policy_actions)
    assert any(
        a.policy_action_type == "permission"
        and a.policy_constraint_type == "purpose"
        and a.policy_constraint_value == "DUO:0000006"
        for a in actions
    )
    assert any(
        a.policy_action_type == "prohibition"
        and a.policy_constraint_type == "temporal"
        and a.temporal_restriction_start == date(2024, 1, 1)
        and a.temporal_restriction_end == date(2024, 12, 31)
        for a in actions
    )
    assert any(
        a.policy_action_type == "permission" and a.policy_constraint_type == "spatial"
        for a in actions
    )
