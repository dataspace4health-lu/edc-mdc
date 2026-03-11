import uuid
import pytest
from fastapi.testclient import TestClient
from main import app
from models.data_service import DataService, DataServiceEndpoint
from models.identity_context import IdentityContext
from schemas.data_service import DataServiceDto, DataServiceEndpointDto
from test_factory import client_with_logged_in_user


def test_get_data_services(db_session, client_with_logged_in_user):
    # Clean up existing data
    db_session.query(DataServiceEndpoint).delete()
    db_session.query(DataService).delete()
    db_session.commit()

    # Create unique titles using UUID
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

    response = client_with_logged_in_user.get("/api/v1/data_services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_data_service_by_id(db_session, client_with_logged_in_user):
    title = f"Test Service - {uuid.uuid4()}"
    service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com", endpoint_description="Test endpoint"
    )
    service.endpoints.append(endpoint)
    db_session.add(service)
    db_session.commit()

    response = client_with_logged_in_user.get(f"/api/v1/data_services/{service.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == title


def test_get_data_service_not_found(db_session, client_with_logged_in_user):
    response = client_with_logged_in_user.get("/api/v1/data_services/999")
    assert response.status_code == 404
    assert "Data Service[999] not found" in response.json()["detail"]


def test_create_data_service(db_session, client_with_logged_in_user):
    unique_title = f"New Service - {uuid.uuid4()}"
    dto = {
        "title": unique_title,
        "endpoints": [
            {
                "endpoint_url": "https://api.example.com/data",
                "endpoint_description": "Test endpoint",
            }
        ],
    }

    response = client_with_logged_in_user.post("/api/v1/data_services", json=dto)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == unique_title
    assert len(data["endpoints"]) == 1
    assert data["endpoints"][0]["endpoint_url"] == "https://api.example.com/data"


def test_create_data_service_duplicate_title(db_session, client_with_logged_in_user):
    title = f"Existing Service - {uuid.uuid4()}"
    existing_service = DataService(title=title)
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/existing",
        endpoint_description="Existing endpoint",
    )
    existing_service.endpoints.append(endpoint)
    db_session.add(existing_service)
    db_session.commit()

    dto = {
        "title": title,
        "endpoints": [
            {
                "endpoint_url": "https://api.example.com/data",
                "endpoint_description": "Test endpoint",
            }
        ],
    }

    response = client_with_logged_in_user.post("/api/v1/data_services", json=dto)
    assert response.status_code == 400
    assert (
        f"Data Service with title '{title}' already exists" in response.json()["detail"]
    )


def test_create_data_service_no_endpoints(db_session, client_with_logged_in_user):
    dto = {"title": f"New Service - {uuid.uuid4()}", "endpoints": []}

    response = client_with_logged_in_user.post("/api/v1/data_services", json=dto)
    assert response.status_code == 400
    assert "Data Service must have at least one endpoint" in response.json()["detail"]


def test_update_data_service(db_session, client_with_logged_in_user):
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

    dto = {
        "title": updated_title,
        "endpoints": [
            {
                "endpoint_url": "https://api.example.com/updated",
                "endpoint_description": "Updated endpoint",
            }
        ],
    }

    response = client_with_logged_in_user.put(
        f"/api/v1/data_services/{service.id}", json=dto
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == updated_title
    assert len(data["endpoints"]) == 1
    assert data["endpoints"][0]["endpoint_url"] == "https://api.example.com/updated"


def test_update_data_service_not_found(db_session, client_with_logged_in_user):
    dto = {
        "title": f"Updated Title - {uuid.uuid4()}",
        "endpoints": [
            {
                "endpoint_url": "https://api.example.com/updated",
                "endpoint_description": "Updated endpoint",
            }
        ],
    }

    response = client_with_logged_in_user.put("/api/v1/data_services/999", json=dto)
    assert response.status_code == 404
    assert "Data Service[999] not found" in response.json()["detail"]
