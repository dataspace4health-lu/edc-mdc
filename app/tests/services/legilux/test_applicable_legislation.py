import pytest
from services.legilux.legislation import LegiluxApplicableLegislationService
from schemas.legilux import LegiluxLegislation


class FakeLegiluxClient:
    def __init__(self, json_payload):
        self._json = json_payload
        self.last_query = None

    async def sparql_json(self, query: str):
        # capture the query so we can assert the lang was injected
        self.last_query = query
        return self._json


@pytest.mark.asyncio
async def test_list_legislations_maps_bindings_to_rows():
    payload = {
        "head": {"vars": ["concept", "notation", "label"]},
        "results": {
            "bindings": [
                {
                    "act": {
                        "value": "http://data.legilux.public.lu/eli/etat/leg/rgd/2022/04/07/a180/jo"  # NOSONAR
                    },
                    "title": {"value": "Règlement grand-ducal du 7 avril 2022."},
                    "description": {
                        "value": "Règlement grand-ducal du 7 avril 2022 déterminant les mesures d'exécution de la loi modifiée du 23 décembre 2016 "
                    },
                }
            ]
        },
    }

    fake = FakeLegiluxClient(payload)
    svc = LegiluxApplicableLegislationService(client=fake)

    results = await svc.list_legislation()
    assert isinstance(results, list)
    assert len(results) == 1
    assert isinstance(results[0], LegiluxLegislation)
    assert (
        results[0].id
        == "http://data.legilux.public.lu/eli/etat/leg/rgd/2022/04/07/a180/jo"  # NOSONAR
    )
    assert (
        results[0].link
        == "http://data.legilux.public.lu/eli/etat/leg/rgd/2022/04/07/a180/jo"  # NOSONAR
    )
    assert results[0].label == "Règlement grand-ducal du 7 avril 2022."
    assert results[0].description.startswith(
        "Règlement grand-ducal du 7 avril 2022 déterminant les mesures d'exécution"
    )


@pytest.mark.asyncio
async def test_list_legislation_empty_results_are_ok():
    payload = {"head": {"vars": []}, "results": {"bindings": []}}
    fake = FakeLegiluxClient(json_payload=payload)
    svc = LegiluxApplicableLegislationService(client=fake)
    results = await svc.list_legislation()
    assert results == []


@pytest.mark.asyncio
async def test_list_legislation_bubbles_client_errors():
    class ExplodingClient:
        async def sparql_json(self, query: str):
            raise RuntimeError("Error")

    svc = LegiluxApplicableLegislationService(client=ExplodingClient())
    with pytest.raises(RuntimeError):
        await svc.list_legislation()


@pytest.mark.asyncio
async def test_list_legislation_respects_limit():
    fake = FakeLegiluxClient({"head": {"vars": []}, "results": {"bindings": []}})
    svc = LegiluxApplicableLegislationService(client=fake)
    await svc.list_legislation(limit=10)
    assert "LIMIT 10" in fake.last_query


def test_normalize_filter_removes_https_protocol():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "https://legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


def test_normalize_filter_removes_http_protocol():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "http://legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"  # NOSONAR
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


def test_normalize_filter_removes_data_subdomain():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "data.legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


def test_normalize_filter_removes_protocol_and_data_subdomain():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "https://data.legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


def test_normalize_filter_handles_http_data_subdomain():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "http://data.legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"  # NOSONAR
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


def test_normalize_filter_leaves_plain_text_unchanged():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "règlement grand-ducal"
    )
    assert result == "règlement grand-ducal"


def test_normalize_filter_handles_empty_string():
    result = LegiluxApplicableLegislationService._normalize_filter("")
    assert result == ""


def test_normalize_filter_handles_url_without_protocol():
    result = LegiluxApplicableLegislationService._normalize_filter(
        "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"
    )
    assert result == "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"


@pytest.mark.asyncio
async def test_list_legislation_with_url_filter_normalized():
    """Test that URL filters are normalized before querying"""
    fake = FakeLegiluxClient({"head": {"vars": []}, "results": {"bindings": []}})
    svc = LegiluxApplicableLegislationService(client=fake)

    # Search with https:// URL
    await svc.list_legislation(
        filter="https://legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo"
    )

    # Verify the query contains the normalized filter (without https://)
    assert "legilux.public.lu/eli/etat/leg/loi/2011/09/02/n1/jo" in fake.last_query
    assert "https://" not in fake.last_query
