import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from conftest import db_session
from fastapi import Request
from models.dataset import Dataset, DatasetContact, DatasetStatus, DatasetCreator
from models.identity_context import IdentityContext
from test_factory import (
    client_with_logged_in_user,
    get_sample_contact,
    get_sample_organisation,
)


def test_get_released_datasets_endpoint(client_with_logged_in_user, db_session):
    # Clear database
    db_session.query(Dataset).delete()
    db_session.commit()

    # Create minimal dataset with released_at
    organisation = get_sample_organisation(db_session)
    # Set accessible_within_ctie to False to match the filter
    organisation.accessible_within_ctie = False
    contact = get_sample_contact(db_session, organisation.id)

    dataset = Dataset(
        title="Test Dataset",
        description="Test Description",
        identifier=str(uuid4()),
        status=DatasetStatus.PUBLISHED.value,
        released_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        publisher_id=organisation.id,
        user_id=1,
    )
    db_session.add(dataset)
    db_session.flush()

    # Add creator using junction table
    dataset_creator = DatasetCreator(
        dataset_id=dataset.id, organisation_id=organisation.id
    )
    dataset.creators.add(dataset_creator)

    db_session.flush()

    dataset_contact = DatasetContact(dataset_id=dataset.id, contact_id=contact.id)
    db_session.add(dataset_contact)
    db_session.commit()
    db_session.refresh(dataset)

    # Store dataset attributes before making API call
    dataset_id = dataset.id
    dataset_identifier = dataset.identifier

    # Mock identity context with system:admin permission
    mock_identity = IdentityContext(
        user_id=1,
        permissions=["system:admin"],
        current_organisation_id=None,
    )

    # Mock the authenticate_service_account_if_present to return None (no service account)
    # and mock the single tenant validation to return our mock identity
    with patch(
        "auth.dependencies.authenticate_service_account_if_present",
        return_value=None,
    ), patch(
        "auth.dependencies.validate_and_retrieve_identity_context_single_tenant",
        return_value=mock_identity,
    ):
        response = client_with_logged_in_user.get(
            "/api/v1/released-datasets?page=1&page_size=10"
        )

        assert response.status_code == 200, response.text

        data = response.json()
        assert "items" in data
        assert "meta" in data

        assert data["meta"]["total_items"] == 1
        assert len(data["items"]) == 1

        item = data["items"][0]
        assert item["id"] == dataset_id
        assert item["identifier"] == dataset_identifier
        assert item["status"] == DatasetStatus.PUBLISHED.value
        assert "released_at" in item
        assert item["released_at"] is not None


def test_get_released_datasets_unauthorized(client_with_logged_in_user, db_session):
    # Test that endpoint returns 403 when user lacks system:admin permission

    # Mock no service account
    with patch(
        "auth.dependencies.authenticate_service_account_if_present",
        return_value=None,
    ), patch(
        "auth.dependencies.validate_and_retrieve_identity_context_single_tenant",
        side_effect=lambda *args, **kwargs: (_ for _ in ()).throw(
            __import__("fastapi").HTTPException(status_code=403, detail="Unauthorized")
        ),
    ):
        response = client_with_logged_in_user.get(
            "/api/v1/released-datasets?page=1&page_size=10"
        )

        assert response.status_code == 403, response.text


def test_get_released_datasets_with_service_account(
    client_with_logged_in_user, db_session
):
    # Clear database
    db_session.query(Dataset).delete()
    db_session.commit()

    # Create test dataset
    organisation = get_sample_organisation(db_session)
    organisation.accessible_within_ctie = False
    contact = get_sample_contact(db_session, organisation.id)

    dataset = Dataset(
        title="Test Dataset",
        description="Test Description",
        identifier=str(uuid4()),
        status=DatasetStatus.PUBLISHED.value,
        released_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        publisher_id=organisation.id,
        user_id=1,
    )
    db_session.add(dataset)
    db_session.flush()

    # Add creator using junction table
    dataset_creator = DatasetCreator(
        dataset_id=dataset.id, organisation_id=organisation.id
    )
    dataset.creators.add(dataset_creator)

    db_session.flush()

    dataset_contact = DatasetContact(dataset_id=dataset.id, contact_id=contact.id)
    db_session.add(dataset_contact)
    db_session.commit()
    db_session.refresh(dataset)

    # Store dataset attributes before making API call
    dataset_id = dataset.id
    dataset_identifier = dataset.identifier

    # Mock service account identity
    mock_service_account_identity = IdentityContext(
        user_id=999,
        permissions=["system:admin"],
        current_organisation_id=None,
    )

    # Mock authenticate_service_account_if_present to return the service account identity
    with patch(
        "auth.dependencies.authenticate_service_account_if_present",
        return_value=mock_service_account_identity,
    ):
        # Make request with service account token
        response = client_with_logged_in_user.get(
            "/api/v1/released-datasets?page=1&page_size=10",
            headers={"Authorization": "Bearer fake-service-account-token"},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "items" in data
        assert "meta" in data
