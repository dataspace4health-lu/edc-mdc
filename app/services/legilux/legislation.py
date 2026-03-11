from __future__ import annotations
from typing import List
from services.legilux.client import LegiluxClient
from schemas.legilux import LegiluxLegislation


class QueryConstants:
    RESULTS = "results"
    BINDINGS = "bindings"
    DESCRIPTION = "description"
    ACT = "act"
    TITLE = "title"
    VALUE = "value"


class LegiluxApplicableLegislationService:
    def __init__(self, client: LegiluxClient | None = None) -> None:
        self.client = client or LegiluxClient()

    @staticmethod
    def _normalize_filter(filter: str) -> str:
        if not filter:
            return filter

        # Remove http://, https://, http://, and common subdomains
        normalized = filter.replace("https://", "").replace("http://", "")  # NOSONAR
        # Remove 'data.' subdomain if present to match both legilux.public.lu and data.legilux.public.lu
        if normalized.startswith("data."):
            normalized = normalized[5:]

        return normalized

    @staticmethod
    def _query_laws(filter: str = "", limit: int = 10) -> str:
        normalized_filter = LegiluxApplicableLegislationService._normalize_filter(
            filter
        )

        sparql_query = """
                PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
                PREFIX dct:   <http://purl.org/dc/terms/>
                PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?act ?description ?title ?altTitle
                WHERE {
                    GRAPH ?g {
                        ?act a jolux:Act ;
                            jolux:inForceStatus <http://data.legilux.public.lu/resource/authority/application-status/in-force> ;
                            jolux:isRealizedBy ?expr .

                        OPTIONAL { ?expr jolux:title       ?description }
                        OPTIONAL { ?expr jolux:titleShort  ?title }
                        OPTIONAL { ?expr dct:title         ?altTitle }
                        OPTIONAL { ?expr rdfs:label        ?label }
        """

        if normalized_filter:
            sparql_query += f"""
                        FILTER (CONTAINS(LCASE(?description), LCASE("{normalized_filter}")) ||
                                CONTAINS(LCASE(STR(?act)), LCASE("{normalized_filter}")) ||
                                CONTAINS(LCASE(?title), LCASE("{normalized_filter}")))
            """

        sparql_query += """
                    }
                }
        """

        # Add LIMIT clause
        if limit > 0:
            sparql_query += f"\nLIMIT {limit}"

        return sparql_query.strip()

    async def list_legislation(
        self, filter: str = "", limit: int = 10
    ) -> List[LegiluxLegislation]:
        query = self._query_laws(filter=filter, limit=limit)
        results = await self.client.sparql_json(query=query)
        legislation_list = []

        for result in results[QueryConstants.RESULTS][QueryConstants.BINDINGS]:
            # Extract values from SPARQL result format
            act = result.get(QueryConstants.ACT, {})
            description = result.get(QueryConstants.DESCRIPTION, {})
            title = result.get(QueryConstants.TITLE, {})

            uri = (
                act.get(QueryConstants.VALUE, "") if isinstance(act, dict) else str(act)
            )
            desc_text = (
                description.get(QueryConstants.VALUE, "")
                if isinstance(description, dict)
                else str(description)
            )
            title_text = (
                title.get(QueryConstants.VALUE, "")
                if isinstance(title, dict)
                else str(title)
            )

            # Use title if available, otherwise use first 100 chars of description
            label = title_text or desc_text[:100] if desc_text else ""

            legislation_list.append(
                LegiluxLegislation(
                    id=uri,
                    label=label,
                    description=desc_text,
                    link=uri,
                )
            )

        return legislation_list
