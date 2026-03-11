import uuid
import pytest
from models.data_service import DataService, DataServiceEndpoint
from repositories.data_service import DataServiceRepository
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
    services = repo.get_data_services()

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
    retrieved_service = repo.get_data_service(service.id)

    assert retrieved_service.id == service.id
    assert retrieved_service.title == title
    assert len(retrieved_service.endpoints) == 1
    assert retrieved_service.endpoints[0].endpoint_url == "https://api.example.com"
    assert retrieved_service.endpoints[0].data_service_id == service.id


def test_get_data_service_not_found(db_session):
    repo = DataServiceRepository(db_session)

    with pytest.raises(HTTPException) as exc_info:
        repo.get_data_service(999)

    assert exc_info.value.status_code == 404
    assert "Data Service[999] not found" in str(exc_info.value.detail)


def test_add_data_service(db_session):
    title = f"New Service - {uuid.uuid4()}"
    service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com", endpoint_description="Test endpoint"
    )
    service.endpoints.append(endpoint)

    repo = DataServiceRepository(db_session)
    repo.add(service)
    repo.commit()

    retrieved_service = db_session.query(DataService).filter_by(title=title).first()
    assert retrieved_service is not None
    assert retrieved_service.title == title
    assert len(retrieved_service.endpoints) == 1
    assert retrieved_service.endpoints[0].endpoint_url == "https://api.example.com"
    assert retrieved_service.endpoints[0].data_service_id == retrieved_service.id


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

    service.title = updated_title
    new_endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/updated",
        endpoint_description="Updated endpoint",
    )
    service.endpoints.clear()
    service.endpoints.append(new_endpoint)

    repo = DataServiceRepository(db_session)
    repo.update(service)
    repo.commit()

    updated_service = db_session.query(DataService).filter_by(id=service.id).first()
    assert updated_service.title == updated_title
    assert len(updated_service.endpoints) == 1
    assert (
        updated_service.endpoints[0].endpoint_url == "https://api.example.com/updated"
    )
    assert updated_service.endpoints[0].data_service_id == original_id

    old_endpoint = (
        db_session.query(DataServiceEndpoint).filter_by(id=original_endpoint_id).first()
    )
    assert old_endpoint is None


def test_add_endpoints(db_session):
    title = f"Test Service - {uuid.uuid4()}"
    service = DataService(title=title)
    db_session.add(service)
    db_session.commit()

    endpoints = [
        DataServiceEndpoint(
            endpoint_url="https://api.example.com/data1",
            endpoint_description="First endpoint",
            data_service_id=service.id,
        ),
        DataServiceEndpoint(
            endpoint_url="https://api.example.com/data2",
            endpoint_description="Second endpoint",
            data_service_id=service.id,
        ),
    ]

    repo = DataServiceRepository(db_session)
    repo.add_endpoints(endpoints)
    repo.commit()

    service = repo.get_data_service(service.id)
    assert len(service.endpoints) == 2
    assert service.endpoints[0].endpoint_url == "https://api.example.com/data1"
    assert service.endpoints[1].endpoint_url == "https://api.example.com/data2"
    assert all(endpoint.data_service_id == service.id for endpoint in service.endpoints)


def test_get_by_title(db_session):
    title = f"Unique Title - {uuid.uuid4()}"
    service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com", endpoint_description="Test endpoint"
    )
    service.endpoints.append(endpoint)
    db_session.add(service)
    db_session.commit()

    repo = DataServiceRepository(db_session)
    retrieved_service = repo.get_by_title(title)

    assert retrieved_service is not None
    assert retrieved_service.title == title
    assert len(retrieved_service.endpoints) == 1
    assert retrieved_service.endpoints[0].endpoint_url == "https://api.example.com"
    assert retrieved_service.endpoints[0].data_service_id == retrieved_service.id

    assert repo.get_by_title("Non Existent Title") is None
