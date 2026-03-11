import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from os import path
import os
from dependencies.database import SessionLocal
from models.data_dictionary import DataDictionaryEntry
from models.distribution import (
    Distribution,
    DistributionAccessUrl,
    DistributionDownloadUrl,
    DistributionLanguage,
    LinkedSchema,
)
from models.dataset_relation import DatasetRelation
from models.activity_log import ActivityLog
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from models.keyword_assignment import KeywordAssignment
from models.dataset import (
    Dataset,
    DatasetAreaOfCompetence,
    DatasetAreaOfWork,
    DatasetCodingSystem,
    DatasetConvention,
    DatasetDataProtectionType,
    DatasetGroupManagers,
    DatasetKeyword,
    DatasetLanguage,
    DatasetApplicableLegislation,
    DatasetPersonalData,
    DatasetSpatialCoverage,
    DatasetSpatialResolution,
    DatasetTheme,
    DatasetType,
    DatasetTypes,
    DatasetProvenanceEntry,
    DatasetVersionNote,
    WasGeneratedBy,
    OtherIdentifier,
)


def pytest_sessionstart(session):
    if path.exists("./test.db"):
        os.remove("./test.db")

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture
def db_session():
    """Create a new database session for testing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_db(db_session):
    db_session.query(ActivityLog).delete()
    db_session.query(LinkedSchema).delete()
    db_session.query(OtherIdentifier).delete()
    db_session.query(WasGeneratedBy).delete()
    db_session.query(DataDictionaryEntry).delete()
    db_session.query(DistributionAccessUrl).delete()
    db_session.query(DistributionDownloadUrl).delete()
    db_session.query(DistributionLanguage).delete()
    db_session.query(Distribution).delete()
    db_session.query(DatasetRelation).delete()
    db_session.query(DatasetTheme).delete()
    db_session.query(DatasetKeyword).delete()
    db_session.query(DatasetLanguage).delete()
    db_session.query(DatasetAreaOfWork).delete()
    db_session.query(DatasetAreaOfCompetence).delete()
    db_session.query(DatasetConvention).delete()
    db_session.query(DatasetDataProtectionType).delete()
    db_session.query(DatasetApplicableLegislation).delete()
    db_session.query(DatasetSpatialCoverage).delete()
    db_session.query(DatasetSpatialResolution).delete()
    db_session.query(DatasetGroupManagers).delete()
    db_session.query(DatasetType).delete()
    db_session.query(DatasetTypes).delete()
    db_session.query(DatasetCodingSystem).delete()
    db_session.query(DatasetPersonalData).delete()
    db_session.query(DatasetProvenanceEntry).delete()
    db_session.query(DatasetVersionNote).delete()
    db_session.query(Dataset).delete()
    db_session.commit()
    yield
