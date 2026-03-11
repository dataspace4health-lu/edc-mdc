import pytest
from fastapi.testclient import TestClient
from services.form_fields_service import FormFieldsService
from test_factory import client_with_logged_in_user
from conftest import db_session
from sqlalchemy.orm import Session
from models.keyword_assignment import KeywordAssignment
from models.applicable_legislation_assignment import ApplicableLegislationAssignment
from models.dataset import Keyword, ApplicableLegislation


@pytest.fixture(autouse=True)
def clean_form_fields(db_session: Session):
    try:
        db_session.rollback()
    except:
        pass

    db_session.query(KeywordAssignment).delete()
    db_session.query(ApplicableLegislationAssignment).delete()
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
    db_session.query(Keyword).delete()
    db_session.query(ApplicableLegislation).delete()
    db_session.commit()


@pytest.fixture
def default_keyword():
    return {
        "eng_label": "Machine Learning",
        "organisation_ids": [1],
    }


@pytest.fixture
def default_applicable_legislation():
    return {
        "eng_label": "Consent",
        "description": "Consent description",
        "link": "https://www.example.com",
        "organisation_ids": [1],
    }


def test_create_keyword(client_with_logged_in_user, default_keyword):
    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword", json=default_keyword
    )
    assert (
        response.status_code == 201
    ), f"Unexpected status code: {response.status_code}, Response: {response.text}"
    created_keyword = response.json()
    assert "key" in created_keyword, "Keyword key not found in response"
    assert created_keyword["eng_label"] == default_keyword["eng_label"]


def test_create_applicable_legislation(
    client_with_logged_in_user, default_applicable_legislation
):
    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/applicable_legislation",
        json=default_applicable_legislation,
    )
    assert (
        response.status_code == 201
    ), f"Unexpected status code: {response.status_code}, Response: {response.text}"
    created_applicable_legislation = response.json()
    assert (
        "key" in created_applicable_legislation
    ), "Applicable Legislation key not found in response"
    assert (
        created_applicable_legislation["eng_label"]
        == default_applicable_legislation["eng_label"]
    )
    assert (
        created_applicable_legislation["description"]
        == default_applicable_legislation["description"]
    )
    assert (
        created_applicable_legislation["link"] == default_applicable_legislation["link"]
    )


def test_get_all_keywords_paginated(client_with_logged_in_user, default_keyword):
    client_with_logged_in_user.post("/api/v1/form-fields/keyword", json=default_keyword)

    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword/all",
        json={
            "page": 1,
            "page_size": 10,
            "query": None,
            "organisation_filters": None,
        },
    )

    assert response.status_code == 200
    result = response.json()

    meta = result["meta"]
    assert meta["page"] == 1
    assert meta["page_size"] == 10
    assert meta["total_items"] >= 1

    keywords = result["items"]
    assert len(keywords) >= 1
    assert any(
        keyword["eng_label"] == default_keyword["eng_label"] for keyword in keywords
    )


def test_update_keyword(client_with_logged_in_user, default_keyword):
    # First create the keyword
    create_response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword", json=default_keyword
    )
    assert create_response.status_code == 201
    created_keyword = create_response.json()

    # Now update it
    updated_keyword = default_keyword.copy()
    updated_keyword["key"] = created_keyword["key"]
    updated_keyword["eng_label"] = "Updated Machine Learning"

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/keyword", json=updated_keyword
    )
    assert response.status_code == 200
    keyword = response.json()
    assert keyword["eng_label"] == updated_keyword["eng_label"]


def test_update_applicable_legislation(
    client_with_logged_in_user, default_applicable_legislation
):
    # First create the applicable legislation
    create_response = client_with_logged_in_user.post(
        "/api/v1/form-fields/applicable_legislation",
        json=default_applicable_legislation,
    )
    assert create_response.status_code == 201
    created_applicable_legislation = create_response.json()

    # Now update it
    updated_applicable_legislation = default_applicable_legislation.copy()
    updated_applicable_legislation["key"] = created_applicable_legislation["key"]
    updated_applicable_legislation["eng_label"] = "Updated Consent"
    updated_applicable_legislation["description"] = "Updated Consent description"
    updated_applicable_legislation["link"] = "https://www.example.com/updated"

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/applicable_legislation",
        json=updated_applicable_legislation,
    )
    assert response.status_code == 200
    applicable_legislation = response.json()
    assert (
        applicable_legislation["eng_label"]
        == updated_applicable_legislation["eng_label"]
    )
    assert (
        applicable_legislation["description"]
        == updated_applicable_legislation["description"]
    )
    assert applicable_legislation["link"] == updated_applicable_legislation["link"]


def test_delete_keyword(client_with_logged_in_user, default_keyword):
    # First create the keyword
    create_response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword", json=default_keyword
    )
    assert create_response.status_code == 201
    created_keyword = create_response.json()

    # Now delete it
    keyword_dto = default_keyword.copy()
    keyword_dto["key"] = created_keyword["key"]

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/keyword/delete", json=keyword_dto
    )
    assert response.status_code == 200

    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword/all",
        json={
            "page": 1,
            "page_size": 10,
            "query": None,
            "organisation_filters": None,
        },
    )
    keywords = response.json()["items"]
    assert not any(keyword["key"] == keyword_dto["key"] for keyword in keywords)


def test_delete_applicable_legislation(
    client_with_logged_in_user, default_applicable_legislation
):
    # First create the applicable legislation
    create_response = client_with_logged_in_user.post(
        "/api/v1/form-fields/applicable_legislation",
        json=default_applicable_legislation,
    )
    assert create_response.status_code == 201
    created_applicable_legislation = create_response.json()

    # Now delete it
    applicable_legislation_dto = default_applicable_legislation.copy()
    applicable_legislation_dto["key"] = created_applicable_legislation["key"]

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/applicable_legislation/delete",
        json=applicable_legislation_dto,
    )
    assert response.status_code == 200

    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/applicable_legislation/all",
        json={
            "page": 1,
            "page_size": 10,
            "query": None,
            "organisation_filters": None,
        },
    )
    applicable_legislation = response.json()["items"]
    assert not any(
        applicable_legislation["key"] == applicable_legislation_dto["key"]
        for applicable_legislation in applicable_legislation
    )


def test_promote_keyword_to_global_route(client_with_logged_in_user, default_keyword):
    keyword_dto = default_keyword.copy()
    keyword_dto["eng_label"] = "Machine Learning 1"
    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/keyword", json=keyword_dto
    )
    assert response.status_code == 201
    created_keyword = response.json()

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/keyword/{created_keyword['key']}/promote-global"
    )
    assert response.status_code == 200

    promoted_field = response.json()
    assert promoted_field["organisation_ids"] == []
    assert promoted_field["key"] == created_keyword["key"]


def test_promote_applicable_legislation_to_global_route(
    client_with_logged_in_user, default_applicable_legislation
):
    applicable_legislation_dto = default_applicable_legislation.copy()
    applicable_legislation_dto["eng_label"] = "Consent 1"
    response = client_with_logged_in_user.post(
        "/api/v1/form-fields/applicable_legislation", json=applicable_legislation_dto
    )
    assert response.status_code == 201
    created_applicable_legislation = response.json()

    response = client_with_logged_in_user.put(
        f"/api/v1/form-fields/applicable_legislation/{created_applicable_legislation['key']}/promote-global"
    )
    assert response.status_code == 200

    promoted_field = response.json()
    assert promoted_field["organisation_ids"] == []
