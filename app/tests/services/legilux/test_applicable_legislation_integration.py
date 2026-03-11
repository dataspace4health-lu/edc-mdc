import pytest
import os
import httpx
from services.legilux.legislation import LegiluxApplicableLegislationService
from services.legilux.client import LegiluxClient
from schemas.legilux import LegiluxLegislation
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_legilux_legislations_live_service_call():
    # """
    #     RUN_LIVE_TESTS=1 pytest
    # """
    if not os.getenv("RUN_LIVE_TESTS"):
        pytest.skip("Live tests disabled. Set RUN_LIVE_TESTS=1 to run.")

    svc = LegiluxApplicableLegislationService(client=LegiluxClient())
    rows = await svc.list_legislation(limit=200)

    assert isinstance(rows, list)
    assert len(rows) > 100
    first = rows[0]
    assert isinstance(first, LegiluxLegislation)
    assert first.id is not None
    assert first.link is not None
    assert first.label is not None


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

        svc = LegiluxApplicableLegislationService(client=LegiluxClient())
        with pytest.raises(httpx.HTTPStatusError):
            await svc.list_legislation()
