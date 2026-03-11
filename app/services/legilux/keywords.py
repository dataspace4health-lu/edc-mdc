from __future__ import annotations
from typing import List, Optional, TypedDict
from services.legilux.client import LegiluxClient


class LegiluxKeywordRow(TypedDict, total=False):
    uri: str
    label: str
    notation: Optional[str]


class LegiluxKeywordsService:
    def __init__(self, client: LegiluxClient | None = None) -> None:
        self.client = client or LegiluxClient()

    @staticmethod
    def _query_keywords(lang: str = "fr") -> str:
        return f"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?concept ?notation ?label
WHERE {{
  ?concept skos:inScheme <http://data.legilux.public.lu/resource/authority/legal-subject-theme> ;
           skos:prefLabel ?label .
  OPTIONAL {{ ?concept skos:notation ?notation }}
  FILTER (lang(?label) = "{lang}")
}}
ORDER BY ?notation ?label
""".strip()

    async def list_keywords(self, lang: str = "fr") -> List[LegiluxKeywordRow]:
        data = await self.client.sparql_json(self._query_keywords(lang))
        out: List[LegiluxKeywordRow] = []
        for b in data.get("results", {}).get("bindings", []):
            out.append(
                {
                    "uri": b["concept"]["value"],
                    "label": b["label"]["value"],
                    "notation": b.get("notation", {}).get("value"),
                }
            )
        return out
