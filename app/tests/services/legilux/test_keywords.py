import pytest
from services.legilux.keywords import LegiluxKeywordsService


class FakeLegiluxClient:
    def __init__(self, json_payload):
        self._json = json_payload
        self.last_query = None

    async def sparql_json(self, query: str):
        # capture the query so we can assert the lang was injected
        self.last_query = query
        return self._json


@pytest.mark.asyncio
async def test_list_keywords_maps_bindings_to_rows():
    payload = {
        "head": {"vars": ["concept", "notation", "label"]},
        "results": {
            "bindings": [
                {
                    "concept": {
                        "type": "uri",
                        "value": "http://.../legal-subject/3337",  # NOSONAR
                    },
                    "notation": {"type": "literal", "value": "3337"},
                    "label": {
                        "type": "literal",
                        "xml:lang": "fr",
                        "value": "Mémorandum d’entente",
                    },
                },
                {
                    "concept": {
                        "type": "uri",
                        "value": "http://.../legal-subject/42",  # NOSONAR
                    },
                    # notation is OPTIONAL in the service; omit it here
                    "label": {
                        "type": "literal",
                        "xml:lang": "fr",
                        "value": "Quelque chose",
                    },
                },
            ]
        },
    }
    fake = FakeLegiluxClient(payload)
    svc = LegiluxKeywordsService(client=fake)

    rows = await svc.list_keywords(lang="fr")

    assert rows == [
        {
            "uri": "http://.../legal-subject/3337",  # NOSONAR
            "label": "Mémorandum d’entente",
            "notation": "3337",
        },
        {
            "uri": "http://.../legal-subject/42",  # NOSONAR
            "label": "Quelque chose",
            "notation": None,
        },
    ]
    # make sure the generated SPARQL contains the language filter
    assert 'FILTER (lang(?label) = "fr")' in fake.last_query


@pytest.mark.asyncio
async def test_list_keywords_empty_results_are_ok():
    fake = FakeLegiluxClient({"head": {"vars": []}, "results": {"bindings": []}})
    svc = LegiluxKeywordsService(client=fake)
    rows = await svc.list_keywords(lang="fr")
    assert rows == []


@pytest.mark.asyncio
async def test_list_keywords_bubbles_client_errors():
    class ExplodingClient:
        async def sparql_json(self, query: str):
            raise RuntimeError("boom")

    svc = LegiluxKeywordsService(client=ExplodingClient())
    with pytest.raises(RuntimeError):
        await svc.list_keywords()
