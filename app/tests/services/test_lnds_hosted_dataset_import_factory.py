"""Test that factory can create LNDSHostedDatasetImportService without errors."""

import pytest
from sqlalchemy.orm import Session

from services.lnds_hosted_dataset_import_factory import (
    create_lnds_hosted_dataset_import_service,
)
from services.lnds_hosted_dataset_import_service import LNDSHostedDatasetImportService


def test_factory_creates_service_with_real_db_session(db_session: Session):
    """Test that factory creates service with all dependencies properly initialized.

    This test uses a real database session to catch initialization errors
    that would occur in production (e.g., missing constructor arguments).
    """
    service = create_lnds_hosted_dataset_import_service(
        db_session=db_session,
        source_url="http://test.com",
        source_instance_name="test-source",
        page_size=50,
    )

    # Verify service was created
    assert isinstance(service, LNDSHostedDatasetImportService)
    assert service.source_instance_url == "http://test.com"
    assert service.source_instance_name == "test-source"

    # Verify core dependencies are initialized
    assert service._dataset_repository is not None
    assert service._dataset_rdf_import_service is not None
    assert service._database_session_manager is not None
    assert service._user_service is not None
    assert service._config_service is not None

    # Verify the RDF import service has all required dependencies
    import_service = service._dataset_rdf_import_service
    assert import_service._dataset_service is not None
    assert import_service._dataset_rdf_mapper is not None
    assert import_service._qualified_attribution_service is not None
    assert import_service._qualified_attribution_rdf_mapper is not None
    assert import_service._dataset_relation_service is not None
    assert import_service._dataset_relation_rdf_mapper is not None
    assert import_service._form_fields_import_service is not None
    assert import_service._contact_import_service is not None

    # Verify contact import service has its dependencies
    contact_import_service = import_service._contact_import_service
    assert contact_import_service._contact_service is not None
    assert contact_import_service._contact_repository is not None
