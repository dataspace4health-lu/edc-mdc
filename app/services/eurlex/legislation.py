from __future__ import annotations
from typing import List
import re
from services.eurlex.client import EurlexClient
from services.eurlex.identifiers import (
    extract_celex_from_input,
    extract_eli_from_input,
)
from schemas.eurlex import EurlexLegislation


class QueryConstants:
    RESULTS = "results"
    REFERENCE = "reference"
    CONTENT = "content"
    TITLE = "title"
    CELEX = "celex"
    LINKS = "links"


class EurlexApplicableLegislationService:
    def __init__(self, client: EurlexClient | None = None) -> None:
        self.client = client or EurlexClient()

    @staticmethod
    def _extract_cellar_uuid(reference: str) -> str | None:
        """
        Extract CELLAR UUID from EUR-Lex reference.

        Reference format: eng_cellar:<uuid>_<lang>
        Example: eng_cellar:e9711ce5-7cbd-11ec-8c40-01aa75ed71a1_en
        Returns: e9711ce5-7cbd-11ec-8c40-01aa75ed71a1
        """
        if not reference:
            return None

        # Remove prefix (eng_cellar:, cellar:, etc.)
        if "cellar:" in reference:
            reference = reference.split("cellar:", 1)[1]

        # Remove language suffix (_en, _fr, etc.)
        if "_" in reference:
            reference = reference.rsplit("_", 1)[0]

        return reference

    @staticmethod
    def _build_expert_query(filter: str = "", limit: int = 10) -> str:
        """
        Build expert query for EUR-Lex web service.

        Examples of expert queries:
        - DN=3*  (all documents starting with sector 3)
        - TI~transport  (title contains 'transport')
        - DN=32000* AND TI~Transport
        - DN=51991IP0963 (search by CELEX)
        """
        if not filter:
            # Default query: search for all legal acts in force
            query = "FM=REGULATION OR FM=DIRECTIVE OR FM=DECISION"
        else:
            # First, check if input contains an ELI identifier
            celex_from_eli = extract_eli_from_input(filter)
            if celex_from_eli:
                # Search by document number (CELEX converted from ELI)
                query = f"DN={celex_from_eli}"
            else:
                # Check if input contains a CELEX identifier
                celex = extract_celex_from_input(filter)
                if celex:
                    # Search by document number (CELEX)
                    query = f"DN={celex}"
                # If filter contains special operators as whole words, use it as-is
                # Otherwise, search in title
                # Check for operators as whole words using word boundaries
                # Pattern checks for: boolean operators (AND/OR/NOT as whole words),
                # special chars (= or ~), or field codes followed by = or ~
                elif re.search(r"\b(AND|OR|NOT)\b|[=~]|\b(DN|TI|FM)[=~]", filter):
                    query = filter
                else:
                    # Simple text search in title
                    query = f"TI~{filter}"

        return query

    async def list_legislation(
        self, filter: str = "", limit: int = 10
    ) -> List[EurlexLegislation]:
        query = self._build_expert_query(filter=filter, limit=limit)
        results = await self.client.search(
            expert_query=query, page=1, page_size=limit, search_language="en"
        )

        legislation_list = []

        for result in results.get(QueryConstants.RESULTS, []):
            reference = result.get(QueryConstants.REFERENCE, "")
            content = result.get(QueryConstants.CONTENT, {})
            links = result.get(QueryConstants.LINKS, [])

            # Extract title and CELEX identifier
            title = content.get(QueryConstants.TITLE, reference)
            celex = content.get(QueryConstants.CELEX)

            # Build EUR-Lex URL
            # Priority order:
            # 1. Use CELEX identifier (most reliable and user-friendly)
            # 2. Use HTML document links from SOAP response
            # 3. Fallback to cellar UUID
            # 4. Last resort: use reference as-is

            link = None

            # First try CELEX (preferred method)
            if celex:
                link = (
                    f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:{celex}"
                )

            # Fallback to document links if no CELEX
            if not link and links:
                for doc_link in links:
                    if doc_link.get("type") == "html":
                        link = doc_link.get("url")
                        break

            # Fallback to cellar UUID construction
            if not link:
                cellar_uuid = self._extract_cellar_uuid(reference)
                if cellar_uuid:
                    link = f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=cellar:{cellar_uuid}"
                else:
                    # Last resort fallback
                    link = f"https://eur-lex.europa.eu/legal-content/EN/ALL/?uri={reference}"

            legislation_list.append(
                EurlexLegislation(
                    id=reference,
                    label=title[:100] if title else reference,  # Limit label length
                    description=title,
                    link=link,
                )
            )

        return legislation_list
