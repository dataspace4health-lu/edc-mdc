import os
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock

from services.legilux.client import LegiluxClient
from services.legilux.keywords import LegiluxKeywordsService


@pytest.mark.asyncio
async def test_service_calls_sparql_and_maps_response():
    # --- arrange response payload ---
    sparql_json = {
        "head": {"vars": ["concept", "notation", "label"]},
        "results": {
            "bindings": [
                {
                    "concept": {
                        "type": "uri",
                        "value": "http://data.legilux.public.lu/resource/authority/legal-subject/3337",  # NOSONAR
                    },
                    "notation": {"type": "literal", "value": "3337"},
                    "label": {
                        "type": "literal",
                        "xml:lang": "fr",
                        "value": "Mémorandum d'entente",
                    },
                }
            ]
        },
    }

    # We'll patch httpx.AsyncClient so `LegiluxClient` never actually hits the network
    with patch("services.legilux.client.httpx.AsyncClient") as MockAsyncClient:
        # The context manager returns this instance:
        client_instance = MagicMock()
        # .post(...) returns an async "response-like" mock (changed from .get)
        response_mock = MagicMock()
        response_mock.raise_for_status = MagicMock()
        response_mock.json = MagicMock(return_value=sparql_json)

        client_instance.post = AsyncMock(
            return_value=response_mock
        )  # Changed from .get
        MockAsyncClient.return_value.__aenter__.return_value = client_instance

        # --- act ---
        svc = LegiluxKeywordsService(client=LegiluxClient())
        rows = await svc.list_keywords(lang="fr")

    # --- assert output mapping ---
    assert rows == [
        {
            "uri": "http://data.legilux.public.lu/resource/authority/legal-subject/3337",  # NOSONAR
            "label": "Mémorandum d'entente",
            "notation": "3337",
        }
    ]

    # --- assert request shape ---
    # We verify the AsyncClient.post() call params (changed from .get)
    assert client_instance.post.await_count == 1
    called_args, called_kwargs = client_instance.post.await_args
    assert called_args[0] == "https://data.legilux.public.lu/sparqlendpoint"

    # Check the form data (changed from params to data)
    data = called_kwargs.get("data") or {}
    assert data.get("format") == "application/sparql-results+json"
    sent_query = data.get("query", "")
    assert (
        "skos:inScheme <http://data.legilux.public.lu/resource/authority/legal-subject-theme>"  # NOSONAR
        in sent_query
    )
    assert 'FILTER (lang(?label) = "fr")' in sent_query

    # Check headers
    headers = called_kwargs.get("headers") or {}
    assert headers.get("Accept") == "application/sparql-results+json"
    assert headers.get("Content-Type") == "application/x-www-form-urlencoded"


@pytest.mark.asyncio
async def test_service_handles_upstream_error():
    # Simulate a 500 coming back from upstream by making raise_for_status() raise
    with patch("services.legilux.client.httpx.AsyncClient") as MockAsyncClient:
        client_instance = MagicMock()

        # Create a real httpx.Request so HTTPStatusError can be constructed nicely
        req = httpx.Request(
            "POST", "https://data.legilux.public.lu/sparqlendpoint"
        )  # Changed to POST
        resp = httpx.Response(500, request=req, text="upstream error")

        def _raise():
            raise httpx.HTTPStatusError("500 Server Error", request=req, response=resp)

        response_mock = MagicMock()
        response_mock.raise_for_status = _raise  # will raise when called

        client_instance.post = AsyncMock(
            return_value=response_mock
        )  # Changed from .get
        MockAsyncClient.return_value.__aenter__.return_value = client_instance

        svc = LegiluxKeywordsService(client=LegiluxClient())
        with pytest.raises(httpx.HTTPStatusError):
            await svc.list_keywords()


@pytest.mark.asyncio
async def test_legilux_keywords_live_service_call():
    # """
    #     RUN_LIVE_TESTS=1 pytest
    # """
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Live tests disabled. Set RUN_LIVE_TESTS=1 to run.")

    svc = LegiluxKeywordsService(client=LegiluxClient())
    rows = await svc.list_keywords(lang="fr")

    # Just do basic sanity checks so we don't depend on exact data
    assert isinstance(rows, list)
    assert len(rows) > 100  # should be thousands
    first = rows[0]
    assert "uri" in first and "label" in first
    assert first["uri"].startswith(
        "http://data.legilux.public.lu/resource/authority/legal-subject/"  # NOSONAR
    )
