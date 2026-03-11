import pytest
import os
import httpx
from services.eurlex.legislation import EurlexApplicableLegislationService
from services.eurlex.client import EurlexClient
from schemas.eurlex import EurlexLegislation
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_eurlex_legislations_live_service_call():
    """
    Live test for EUR-Lex legislation service.
    RUN_LIVE_TESTS=1 pytest app/tests/services/eurlex/test_applicable_legislation_integration.py::test_eurlex_legislations_live_service_call -v
    """
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Live tests disabled. Set RUN_LIVE_TESTS=1 to run.")

    svc = EurlexApplicableLegislationService(client=EurlexClient())
    rows = await svc.list_legislation(limit=10)

    assert isinstance(rows, list)
    assert len(rows) > 0
    first = rows[0]
    assert isinstance(first, EurlexLegislation)
    assert first.id is not None
    assert first.link is not None
    assert first.label is not None


@pytest.mark.asyncio
async def test_service_handles_upstream_error():
    """Test that the service properly handles upstream errors"""
    with patch("services.eurlex.client.httpx.AsyncClient") as MockAsyncClient:
        client_instance = MagicMock()

        # Create a real httpx.Request so HTTPStatusError can be constructed
        req = httpx.Request("POST", "https://eur-lex.europa.eu/EURLexWebService")
        resp = httpx.Response(500, request=req, text="upstream error")

        def _raise():
            raise httpx.HTTPStatusError("500 Server Error", request=req, response=resp)

        response_mock = MagicMock()
        response_mock.raise_for_status = _raise

        client_instance.post = AsyncMock(return_value=response_mock)
        MockAsyncClient.return_value.__aenter__.return_value = client_instance

        svc = EurlexApplicableLegislationService(client=EurlexClient())
        with pytest.raises(httpx.HTTPStatusError):
            await svc.list_legislation()


@pytest.mark.asyncio
async def test_service_with_filter():
    """Test the service with a filter query"""
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Live tests disabled. Set RUN_LIVE_TESTS=1 to run.")

    svc = EurlexApplicableLegislationService(client=EurlexClient())

    # Test with a simple text filter
    rows = await svc.list_legislation(filter="transport", limit=5)

    assert isinstance(rows, list)
    if len(rows) > 0:
        first = rows[0]
        assert isinstance(first, EurlexLegislation)
        assert first.id is not None


@pytest.mark.asyncio
async def test_service_with_expert_query():
    """Test the service with expert query syntax"""
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Live tests disabled. Set RUN_LIVE_TESTS=1 to run.")

    svc = EurlexApplicableLegislationService(client=EurlexClient())

    # Test with expert query syntax
    rows = await svc.list_legislation(
        filter="FM=REGULATION AND TI~environment", limit=5
    )

    assert isinstance(rows, list)
    if len(rows) > 0:
        first = rows[0]
        assert isinstance(first, EurlexLegislation)
        assert first.id is not None
