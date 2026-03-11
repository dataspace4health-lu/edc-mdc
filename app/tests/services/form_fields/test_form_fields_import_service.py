import pytest
import uuid
from sqlalchemy.orm import Session
from services.form_fields.form_fields_import_service import FormFieldsImportService
from services.form_fields_permission import FormFieldsPermissionsService
from repositories.keyword import KeywordRepository
from repositories.applicable_legislation import ApplicableLegislationRepository
from repositories.dataset import DatasetRepository
from repositories.distribution import DistributionRepository
from repositories.organisation import OrganisationRepository
from repositories.user_assignment import UserAssignmentRepository
from repositories.keyword_assignment import KeywordAssignmentRepository
from repositories.applicable_legislation_assignment import (
    ApplicableLegislationAssignmentRepository,
)
from models.dataset import Keyword
from models.applicable_legislation import ApplicableLegislation
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from services.activity_log import ActivityLogService
from services.emails.organisation_specific_email import (
    OrganisationSpecificEmailsService,
)
from unittest.mock import MagicMock


def unique_label(prefix="Test"):
    return f"{prefix} {uuid.uuid4().hex[:8]}"


def unique_key(prefix="test"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def mock_activity_log_service():
    return MagicMock(spec=ActivityLogService)


@pytest.fixture
def form_fields_import_service(
    db_session: Session, mock_activity_log_service
) -> FormFieldsImportService:
    keyword_repo = KeywordRepository(db_session)
    keyword_assignment_repo = KeywordAssignmentRepository(db_session)
    dataset_repo = DatasetRepository(db_session)
    applicable_legislation_repo = ApplicableLegislationRepository(db_session)
    applicable_legislation_assignment_repo = ApplicableLegislationAssignmentRepository(
        db_session
    )
    distribution_repo = DistributionRepository(db_session)
    organisation_repo = OrganisationRepository(db_session)
    user_assignment_repo = UserAssignmentRepository(db_session)

    form_fields_permissions_service = FormFieldsPermissionsService(
        keyword_repository=keyword_repo,
        keyword_assignment_repository=keyword_assignment_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repo,
        user_assignment_repository=user_assignment_repo,
    )

    mock_email_service = MagicMock(spec=OrganisationSpecificEmailsService)

    return FormFieldsImportService(
        keyword_repository=keyword_repo,
        keyword_assignment_repository=keyword_assignment_repo,
        dataset_repository=dataset_repo,
        applicable_legislation_repository=applicable_legislation_repo,
        applicable_legislation_assignment_repository=applicable_legislation_assignment_repo,
        distribution_repository=distribution_repo,
        organisation_repository=organisation_repo,
        form_fields_permissions_service=form_fields_permissions_service,
        activity_log_service=mock_activity_log_service,
        email_service=mock_email_service,
    )


def test_ensure_keyword_exists_creates_new_keyword(
    form_fields_import_service: FormFieldsImportService,
    db_session: Session,
):
    label = unique_label("Climate")
    keyword_key = form_fields_import_service.ensure_keyword_exists(
        keyword_value=label,
        organisation_id=1,
        created_by_id=999,
    )

    keyword = db_session.query(Keyword).filter_by(key=keyword_key).first()
    assert keyword is not None
    assert keyword.eng_label == label
    assert keyword.created_by_id == 999


def test_ensure_keyword_exists_finds_by_label(
    form_fields_import_service: FormFieldsImportService,
    db_session: Session,
):
    kw_key = unique_key("test")
    kw_label = unique_label("Test")
    existing_keyword = Keyword(
        key=kw_key,
        eng_label=kw_label,
        created_by_id=1,
    )
    db_session.add(existing_keyword)
    db_session.commit()

    keyword_key = form_fields_import_service.ensure_keyword_exists(
        keyword_value=kw_label,
        organisation_id=1,
        created_by_id=999,
    )

    assert keyword_key == kw_key


def test_ensure_applicable_legislation_exists_creates_new(
    form_fields_import_service: FormFieldsImportService,
    db_session: Session,
):
    url = f"https://example.com/law/{uuid.uuid4().hex[:8]}"
    applicable_legislation_key = (
        form_fields_import_service.ensure_applicable_legislation_exists(
            applicable_legislation_key=url,
            organisation_id=1,
            created_by_id=999,
            title="GDPR",
            link=url,
        )
    )

    assert applicable_legislation_key == url

    applicable_legislation = (
        db_session.query(ApplicableLegislation)
        .filter_by(key=applicable_legislation_key)
        .first()
    )
    assert applicable_legislation is not None
    assert applicable_legislation.eng_label == "GDPR"


def test_ensure_keywords_batch(
    form_fields_import_service: FormFieldsImportService,
    db_session: Session,
):
    keyword_values = {unique_label("A"), unique_label("B"), unique_label("C")}

    result_keys = form_fields_import_service.ensure_keywords_exist(
        keyword_values=keyword_values,
        organisation_id=1,
        created_by_id=999,
    )

    assert len(result_keys) == 3


def test_ensure_applicable_legislations_batch(
    form_fields_import_service: FormFieldsImportService,
    db_session: Session,
):
    applicable_legislation_keys = {
        f"https://example.com/law/{uuid.uuid4().hex[:8]}",
        f"https://example.com/law/{uuid.uuid4().hex[:8]}",
    }

    result_keys = form_fields_import_service.ensure_applicable_legislations_exist(
        applicable_legislation_keys=applicable_legislation_keys,
        organisation_id=1,
        created_by_id=999,
    )

    assert len(result_keys) == 2
