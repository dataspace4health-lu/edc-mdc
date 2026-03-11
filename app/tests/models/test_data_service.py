import pytest
from models.data_service import DataService, DataServiceEndpoint


def test_data_service_endpoint_creation(db_session):
    service = DataService(title="Test Service")
    db_session.add(service)
    db_session.commit()

    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test API endpoint",
        data_service_id=service.id,
    )
    db_session.add(endpoint)
    db_session.commit()

    assert endpoint.id is not None
    assert endpoint.endpoint_url == "https://api.example.com/data"
    assert endpoint.endpoint_description == "Test API endpoint"
    assert endpoint.data_service_id == service.id
    assert endpoint.data_service == service


def test_data_service_creation(db_session):
    service = DataService(title="Test Service")
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test endpoint",
    )
    service.endpoints.append(endpoint)

    db_session.add(service)
    db_session.commit()

    assert service.id is not None
    assert service.title == "Test Service"
    assert len(service.endpoints) == 1
    assert service.endpoints[0].data_service_id == service.id
    assert service.endpoints[0].endpoint_url == "https://api.example.com/data"


def test_data_service_with_endpoints(db_session):
    service = DataService(title="Test Service")
    endpoint1 = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data1",
        endpoint_description="First endpoint",
    )
    endpoint2 = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data2",
        endpoint_description="Second endpoint",
    )
    service.endpoints.extend([endpoint1, endpoint2])

    db_session.add(service)
    db_session.commit()

    assert service.id is not None
    assert len(service.endpoints) == 2
    assert service.endpoints[0].endpoint_url == "https://api.example.com/data1"
    assert service.endpoints[1].endpoint_url == "https://api.example.com/data2"
    assert all(endpoint.data_service_id == service.id for endpoint in service.endpoints)


def test_data_service_equality(db_session):
    service1 = DataService(title="Test Service")
    service2 = DataService(title="Test Service")

    endpoint1 = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test endpoint",
    )
    endpoint2 = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test endpoint",
    )

    service1.endpoints.append(endpoint1)
    service2.endpoints.append(endpoint2)

    db_session.add_all([service1, service2])
    db_session.commit()

    assert service1 == service2

    service2.endpoints[0].endpoint_url = "https://api.example.com/different"
    db_session.commit()
    assert service1 != service2


def test_data_service_to_dict(db_session):
    service = DataService(title="Test Service")
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test endpoint",
    )
    service.endpoints.append(endpoint)

    db_session.add(service)
    db_session.commit()

    service_dict = service.to_dict_for_diff()
    assert service_dict["title"] == "Test Service"
    assert len(service_dict["endpoints"]) == 1
    assert service_dict["endpoints"][0]["url"] == "https://api.example.com/data"
    assert service_dict["endpoints"][0]["description"] == "Test endpoint"


def test_cascade_delete(db_session):
    service = DataService(title="Test Service")
    endpoint = DataServiceEndpoint(
        endpoint_url="https://api.example.com/data",
        endpoint_description="Test endpoint",
    )
    service.endpoints.append(endpoint)

    db_session.add(service)
    db_session.commit()

    endpoint_id = endpoint.id

    db_session.delete(service)
    db_session.commit()

    assert (
        db_session.query(DataServiceEndpoint).filter_by(id=endpoint_id).first() is None
    )
