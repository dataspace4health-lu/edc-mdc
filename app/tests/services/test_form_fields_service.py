import pytest
import uuid
from sqlalchemy.orm import Session
from services.form_fields_service import FormFieldsService
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
from schemas.form_field import (
    FormFieldDto,
    ApplicableLegislationFormFieldDto,
    CreateFormFieldDto,
    CreateApplicableLegislationFormFieldDto,
)
from models.dataset import Theme, Keyword, ApplicableLegislation
from models.identity_context import IdentityContext
from fastapi import HTTPException
from services.activity_log import ActivityLogService
from services.emails.organisation_specific_email import (
    OrganisationSpecificEmailsService,
)
from unittest.mock import MagicMock
from utils.key_generator import KeyGenerator


def generate_unique_key(prefix="test"):
    return f"{prefix}-{str(uuid.uuid4())[:8]}"


@pytest.fixture
def global_identity():
    return IdentityContext(
        user_id=123, permissions=["form-fields:edit", "roles:manage"]
    )


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    try:
        db_session.rollback()
    except:
        pass

    from models.keyword_assignment import KeywordAssignment
    from models.applicable_legislation_assignment import (
        ApplicableLegislationAssignment,
    )

    db_session.query(KeywordAssignment).delete()
    db_session.query(ApplicableLegislationAssignment).delete()
    db_session.query(Theme).delete()
    db_session.query(Keyword).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.commit()

    yield

    try:
        db_session.rollback()
    except:
        pass

    db_session.query(KeywordAssignment).delete()
    db_session.query(ApplicableLegislationAssignment).delete()
    db_session.query(Theme).delete()
    db_session.query(Keyword).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.commit()


@pytest.fixture
def form_fields_service(db_session: Session) -> FormFieldsService:
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

    mock_activity_log_service = MagicMock(spec=ActivityLogService)
    mock_email_service = MagicMock(spec=OrganisationSpecificEmailsService)

    return FormFieldsService(
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


@pytest.fixture
def identity():
    return IdentityContext(user_id=123, permissions=["form-fields:edit"])


@pytest.fixture
def create_form_field_dto() -> CreateFormFieldDto:
    return CreateFormFieldDto(
        eng_label="Eng Label",
        organisation_ids=[1],
    )


@pytest.fixture
def form_field_dto() -> FormFieldDto:
    return FormFieldDto(
        key="eng_label",
        eng_label="Eng Label",
        organisation_ids=[1],
    )


@pytest.fixture
def create_applicable_legislation_dto() -> CreateApplicableLegislationFormFieldDto:
    return CreateApplicableLegislationFormFieldDto(
        eng_label="Artificial Intelligence",
        description="AI description",
        link="https://ai.com",
        organisation_ids=[1],
    )


@pytest.fixture
def applicable_legislation_dto() -> ApplicableLegislationFormFieldDto:
    return ApplicableLegislationFormFieldDto(
        key="artificial_intelligence",
        eng_label="Artificial Intelligence",
        description="AI description",
        link="https://ai.com",
        organisation_ids=[1],
    )


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
    ],
)
def test_create_valid_field_type(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_form_field_dto: CreateFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        field_type, create_form_field_dto, identity
    )
    assert created_field.key == "eng_label"
    assert created_field.eng_label == create_form_field_dto.eng_label
    assert created_field.created_by_id == identity.user_id


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
    ],
)
def test_get_all_valid_field_type(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_form_field_dto: CreateFormFieldDto,
    identity: IdentityContext,
):
    form_fields_service.create(field_type, create_form_field_dto, identity)
    fields = form_fields_service.get_all(field_type, identity)
    assert len(fields) == 1
    assert fields[0].key == "eng_label"


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
    ],
)
def test_get_all_paginated_valid_field_type(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_form_field_dto: CreateFormFieldDto,
    identity: IdentityContext,
):
    form_fields_service.create(field_type, create_form_field_dto, identity)
    paginated_fields = form_fields_service.get_all_paginated(
        field_type, page=1, page_size=10, identity=identity
    )
    assert len(paginated_fields.items) == 1
    assert paginated_fields.items[0].key == "eng_label"
    assert paginated_fields.meta.total_items == 1


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
    ],
)
def test_update_valid_field_type(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_form_field_dto: CreateFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        field_type, create_form_field_dto, identity
    )
    updated_field_dto = FormFieldDto(
        key=created_field.key,
        eng_label=f"Updated Label {generate_unique_key()}",
        organisation_ids=[1],
    )
    updated_field = form_fields_service.update(field_type, updated_field_dto, identity)
    assert updated_field.key == created_field.key
    assert updated_field.eng_label == updated_field_dto.eng_label


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
    ],
)
def test_delete_valid_field_type(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_form_field_dto: CreateFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        field_type, create_form_field_dto, identity
    )
    form_fields_service.delete(field_type, created_field.key, identity)
    fields = form_fields_service.get_all(field_type, identity)
    assert len(fields) == 0


@pytest.mark.parametrize(
    "field_type",
    [
        ("keyword"),
        ("applicable_legislation"),
    ],
)
def test_delete_field_not_found(
    field_type: str, form_fields_service: FormFieldsService, identity: IdentityContext
):
    with pytest.raises(HTTPException) as excinfo:
        form_fields_service.delete(field_type, "non_existent_key", identity)
    assert excinfo.value.status_code == 404


def test_unsupported_field_type(
    form_fields_service: FormFieldsService, identity: IdentityContext
):
    with pytest.raises(ValueError):
        form_fields_service.get_all("unsupported_type", identity)

    with pytest.raises(HTTPException):
        form_fields_service.create(
            "unsupported_type",
            CreateFormFieldDto(
                eng_label="Test",
                organisation_ids=[1],
            ),
            identity,
        )

    with pytest.raises(ValueError):
        form_fields_service.update(
            "unsupported_type",
            FormFieldDto(
                key="test",
                eng_label="Test",
                organisation_ids=[1],
            ),
            identity,
        )

    with pytest.raises(ValueError):
        form_fields_service.delete("unsupported_type", "test", identity)


def test_create_valid_applicable_legislation_field(
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        "applicable_legislation", create_applicable_legislation_dto, identity
    )
    expected_key = KeyGenerator.generate_key_from_label_and_link(
        create_applicable_legislation_dto.eng_label,
        create_applicable_legislation_dto.link,
    )
    assert created_field.key == expected_key
    assert created_field.eng_label == create_applicable_legislation_dto.eng_label
    assert created_field.description == create_applicable_legislation_dto.description
    assert created_field.link == create_applicable_legislation_dto.link
    assert created_field.created_by_id == identity.user_id


def test_get_all_valid_applicable_legislation_field(
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        "applicable_legislation", create_applicable_legislation_dto, identity
    )
    fields = form_fields_service.get_all("applicable_legislation", identity)
    assert len(fields) == 1
    assert fields[0].key == created_field.key


@pytest.mark.parametrize(
    "field_type",
    [
        ("applicable_legislation"),
    ],
)
def test_get_all_paginated(
    field_type: str,
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        field_type, create_applicable_legislation_dto, identity
    )

    paginated_fields = form_fields_service.get_all_paginated(
        field_type, page=1, page_size=10, identity=identity
    )
    assert len(paginated_fields.items) == 1
    assert paginated_fields.items[0].key == created_field.key
    assert paginated_fields.meta.total_items == 1


def test_get_all_valid_applicable_legislation_field(
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        "applicable_legislation", create_applicable_legislation_dto, identity
    )
    fields = form_fields_service.get_all("applicable_legislation", identity)
    assert len(fields) == 1
    assert fields[0].key == created_field.key


def test_update_valid_applicable_legislation_field(
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        "applicable_legislation", create_applicable_legislation_dto, identity
    )
    updated_field_dto = ApplicableLegislationFormFieldDto(
        key=created_field.key,
        eng_label="Updated Label",
        description="Updated Description",
        link="https://updated.com",
        organisation_ids=[1],
    )
    updated_field = form_fields_service.update(
        "applicable_legislation", updated_field_dto, identity
    )
    assert updated_field.key == created_field.key
    assert updated_field.eng_label == updated_field_dto.eng_label
    assert updated_field.description == updated_field_dto.description
    assert updated_field.link == updated_field_dto.link


def test_delete_valid_applicable_legislation_field(
    form_fields_service: FormFieldsService,
    create_applicable_legislation_dto: CreateApplicableLegislationFormFieldDto,
    identity: IdentityContext,
):
    created_field = form_fields_service.create(
        "applicable_legislation", create_applicable_legislation_dto, identity
    )
    form_fields_service.delete("applicable_legislation", created_field.key, identity)
    fields = form_fields_service.get_all("applicable_legislation", identity)
    assert len(fields) == 0


def test_create_keyword_assigns_to_multiple_organizations(
    form_fields_service: FormFieldsService,
    identity: IdentityContext,
):
    keyword_dto_org1 = CreateFormFieldDto(
        eng_label="Shared Keyword",
        organisation_ids=[1],
    )

    created_field_org1 = form_fields_service.create(
        "keyword", keyword_dto_org1, identity
    )
    assert created_field_org1.organisation_ids == [1]

    keyword_dto_org2 = CreateFormFieldDto(
        eng_label="Shared Keyword",
        organisation_ids=[2],
    )

    created_field_org2 = form_fields_service.create(
        "keyword", keyword_dto_org2, identity
    )

    assert set(created_field_org2.organisation_ids) == {1, 2}

    all_keywords = form_fields_service.get_all("keyword", identity)
    assert len(all_keywords) == 1
    assert set(all_keywords[0].organisation_ids) == {1, 2}


def test_create_global_keyword_throws_error_when_already_exists(
    form_fields_service: FormFieldsService,
    global_identity: IdentityContext,
):
    global_keyword_dto = CreateFormFieldDto(
        eng_label="Global Keyword",
        organisation_ids=[],
    )

    created_field = form_fields_service.create(
        "keyword", global_keyword_dto, global_identity
    )
    assert created_field.organisation_ids == []

    duplicate_keyword_dto = CreateFormFieldDto(
        eng_label="Global Keyword",
        organisation_ids=[],
    )

    with pytest.raises(HTTPException) as excinfo:
        form_fields_service.create("keyword", duplicate_keyword_dto, global_identity)

    assert excinfo.value.status_code == 400
    assert "already exists and is global" in str(excinfo.value.detail)


def test_promote_keyword_to_global_success(
    form_fields_service: FormFieldsService,
    global_identity: IdentityContext,
):
    keyword_dto = CreateFormFieldDto(
        eng_label="Keyword to Promote",
        organisation_ids=[1],
    )

    created_field = form_fields_service.create("keyword", keyword_dto, global_identity)
    assert created_field.organisation_ids == [1]

    promoted_field = form_fields_service.promote_to_global(
        "keyword", "keyword_to_promote", global_identity
    )

    assert promoted_field.organisation_ids == []
    assert promoted_field.key == "keyword_to_promote"
    assert promoted_field.eng_label == keyword_dto.eng_label


def test_promote_applicable_legislation_to_global_success(
    form_fields_service: FormFieldsService,
    global_identity: IdentityContext,
):
    applicable_legislation_dto = CreateApplicableLegislationFormFieldDto(
        eng_label="Applicable Legislation to Promote",
        description="Description",
        link="https://example.com",
        organisation_ids=[1, 2],
    )

    created_field = form_fields_service.create(
        "applicable_legislation", applicable_legislation_dto, global_identity
    )
    assert set(created_field.organisation_ids) == {1, 2}

    promoted_field = form_fields_service.promote_to_global(
        "applicable_legislation", created_field.key, global_identity
    )

    assert promoted_field.organisation_ids == []


def test_promote_to_global_permission_denied(
    form_fields_service: FormFieldsService, identity: IdentityContext
):
    wrong_identity = IdentityContext(
        user_id=123, permissions=["form-fields:edit:organisation"]
    )
    keyword_dto = CreateFormFieldDto(
        eng_label="Cannot Promote",
        organisation_ids=[1],
    )

    created_field = form_fields_service.create("keyword", keyword_dto, identity)

    with pytest.raises(HTTPException) as excinfo:
        form_fields_service.promote_to_global(
            "keyword", "cannot_promote", wrong_identity
        )

    assert excinfo.value.status_code == 403
    assert "Only Catalogue Managers can promote" in str(excinfo.value.detail)


def test_promote_already_global_field_error(
    form_fields_service: FormFieldsService,
    global_identity: IdentityContext,
):
    global_keyword_dto = CreateFormFieldDto(
        eng_label="Already Global",
        organisation_ids=[],
    )

    created_field = form_fields_service.create(
        "keyword", global_keyword_dto, global_identity
    )
    assert created_field.organisation_ids == []

    with pytest.raises(HTTPException) as excinfo:
        form_fields_service.promote_to_global(
            "keyword", "already_global", global_identity
        )

    assert excinfo.value.status_code == 400
    assert "already global" in str(excinfo.value.detail)


def test_create_applicable_legislation_with_matching_link_appends_organization(
    form_fields_service: FormFieldsService,
    global_identity: IdentityContext,
):
    # Create first applicable legislation with specific link and organization
    applicable_legislation_dto_org1 = CreateApplicableLegislationFormFieldDto(
        eng_label="Privacy Policy",
        description="First privacy description",
        link="https://privacy.example.com",
        organisation_ids=[1],
    )

    created_field_org1 = form_fields_service.create(
        "applicable_legislation", applicable_legislation_dto_org1, global_identity
    )
    assert created_field_org1.organisation_ids == [1]
    expected_key = KeyGenerator.generate_key_from_label_and_link(
        applicable_legislation_dto_org1.eng_label, applicable_legislation_dto_org1.link
    )
    assert created_field_org1.key == expected_key

    # Create second applicable legislation with different label but same link
    applicable_legislation_dto_org2 = CreateApplicableLegislationFormFieldDto(
        eng_label="Data Protection Policy",
        description="Second privacy description",
        link="https://privacy.example.com",  # Same link as first
        organisation_ids=[2],
    )

    created_field_org2 = form_fields_service.create(
        "applicable_legislation", applicable_legislation_dto_org2, global_identity
    )

    # Should append org 2 to existing applicable legislation instead of creating new one
    assert set(created_field_org2.organisation_ids) == {1, 2}
    assert created_field_org2.key == expected_key  # Should keep original key
    assert (
        created_field_org2.eng_label == "Privacy Policy"
    )  # Should keep original label

    # Verify only one applicable legislation exists in total
    all_applicable_legislations = form_fields_service.get_all(
        "applicable_legislation", global_identity
    )
    assert len(all_applicable_legislations) == 1
    assert set(all_applicable_legislations[0].organisation_ids) == {1, 2}
