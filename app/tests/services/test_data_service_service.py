import uuid
import pytest
from models.data_service import DataService, DataServiceEndpoint
from services.data_service import DataServiceService
from repositories.data_service import DataServiceRepository
from schemas.data_service import DataServiceDto, DataServiceEndpointDto
from fastapi import HTTPException


def test_get_data_services(db_session):
    # Clean up existing data
    db_session.query(DataServiceEndpoint).delete()
    db_session.query(DataService).delete()
    db_session.commit()

    service1 = DataService(title=f"Service 1 - {uuid.uuid4()}")
    service2 = DataService(title=f"Service 2 - {uuid.uuid4()}")

    endpoint1 = DataServiceEndpoint(
        endpoint_url="https://api1.example.com", endpoint_description="Endpoint 1"
    )
    endpoint2 = DataServiceEndpoint(
        endpoint_url="https://api2.example.com", endpoint_description="Endpoint 2"
    )

    service1.endpoints.append(endpoint1)
    service2.endpoints.append(endpoint2)

    db_session.add_all([service1, service2])
    db_session.commit()

    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)
    services = service.get_data_services()

    assert len(services) == 2
    assert len(services[0].endpoints) == 1
    assert len(services[1].endpoints) == 1


def test_get_data_service(db_session):
    title = f"Test Service - {uuid.uuid4()}"
    service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com", endpoint_description="Test endpoint"
    )
    service.endpoints.append(endpoint)
    db_session.add(service)
    db_session.commit()

    repo = DataServiceRepository(db_session)
    service_layer = DataServiceService(repo)
    retrieved_service = service_layer.get_data_service(service.id)

    assert retrieved_service.title == title
    assert len(retrieved_service.endpoints) == 1
    assert (
        list(retrieved_service.endpoints)[0].endpoint_url == "https://api.example.com"
    )


def test_get_data_service_not_found(db_session):
    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)

    with pytest.raises(HTTPException) as exc_info:
        service.get_data_service(999)

    assert exc_info.value.status_code == 404
    assert "Data Service[999] not found" in str(exc_info.value.detail)


def test_create_data_service(db_session):
    title = f"New Service - {uuid.uuid4()}"
    dto = DataServiceDto(
        title=title,
        endpoints=[
            DataServiceEndpointDto(
                endpoint_url="https://api.example.com/data",
                endpoint_description="Test endpoint",
            )
        ],
    )

    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)
    created_service = service.create_data_service(dto)

    assert created_service.title == title
    assert len(created_service.endpoints) == 1
    assert (
        list(created_service.endpoints)[0].endpoint_url
        == "https://api.example.com/data"
    )

    db_service = db_session.query(DataService).filter_by(id=created_service.id).first()
    assert db_service is not None
    assert len(db_service.endpoints) == 1
    assert list(db_service.endpoints)[0].data_service_id == db_service.id


def test_create_data_service_duplicate_title(db_session):
    title = f"Existing Service - {uuid.uuid4()}"
    existing_service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/existing",
        endpoint_description="Existing endpoint",
    )
    existing_service.endpoints.append(endpoint)
    db_session.add(existing_service)
    db_session.commit()

    dto = DataServiceDto(
        title=title,
        endpoints=frozenset(
            [
                DataServiceEndpointDto(
                    endpoint_url="https://api.example.com/data",
                    endpoint_description="Test endpoint",
                )
            ]
        ),
    )

    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)

    with pytest.raises(HTTPException) as exc_info:
        service.create_data_service(dto)

    assert exc_info.value.status_code == 400
    assert f"Data Service with title '{title}' already exists" in str(
        exc_info.value.detail
    )


def test_create_data_service_no_endpoints(db_session):
    title = f"New Service - {uuid.uuid4()}"
    dto = DataServiceDto(title=title, endpoints=[])

    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)

    with pytest.raises(HTTPException) as exc_info:
        service.create_data_service(dto)

    assert exc_info.value.status_code == 400
    assert "Data Service must have at least one endpoint" in str(exc_info.value.detail)


def test_update_data_service(db_session):
    original_title = f"Original Title - {uuid.uuid4()}"
    updated_title = f"Updated Title - {uuid.uuid4()}"

    service = DataService(title=original_title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/original",
        endpoint_description="Original endpoint",
    )
    service.endpoints.append(endpoint)
    db_session.add(service)
    db_session.commit()

    original_id = service.id
    original_endpoint_id = endpoint.id

    dto = DataServiceDto(
        title=updated_title,
        endpoints=[
            DataServiceEndpointDto(
                endpoint_url="https://api.example.com/updated",
                endpoint_description="Updated endpoint",
            )
        ],
    )

    repo = DataServiceRepository(db_session)
    service_layer = DataServiceService(repo)
    updated_service = service_layer.update_data_service(service.id, dto)

    assert updated_service.title == updated_title
    assert len(updated_service.endpoints) == 1
    assert (
        list(updated_service.endpoints)[0].endpoint_url
        == "https://api.example.com/updated"
    )
    assert updated_service.id == original_id  # ID should remain the same

    db_service = db_session.query(DataService).filter_by(id=original_id).first()
    assert db_service is not None
    assert len(db_service.endpoints) == 1
    assert db_service.endpoints[0].data_service_id == original_id

    old_endpoint = (
        db_session.query(DataServiceEndpoint).filter_by(id=original_endpoint_id).first()
    )
    assert old_endpoint is None


def test_update_data_service_not_found(db_session):
    title = f"Updated Title - {uuid.uuid4()}"
    dto = DataServiceDto(
        title=title,
        endpoints=frozenset(
            [
                DataServiceEndpointDto(
                    endpoint_url="https://api.example.com/updated",
                    endpoint_description="Updated endpoint",
                )
            ]
        ),
    )

    repo = DataServiceRepository(db_session)
    service = DataServiceService(repo)

    with pytest.raises(HTTPException) as exc_info:
        service.update_data_service(999, dto)

    assert exc_info.value.status_code == 404
    assert "Data Service[999] not found" in str(exc_info.value.detail)
