from __future__ import annotations
from typing import Any, Dict, Optional
import httpx
import os


class LegiluxClient:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        timeout_sec: float = 30.0,
    ) -> None:
        self.endpoint = endpoint or os.getenv(
            "LEGILUX_ENDPOINT", "https://data.legilux.public.lu/sparqlendpoint"
        )
        self.timeout = timeout_sec

    async def sparql_json(self, query: str) -> Dict[str, Any]:
        # Use POST method with form data
        data = {
            "query": query,
            "format": "application/sparql-results+json",
        }
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.endpoint, data=data, headers=headers)
            resp.raise_for_status()
            return resp.json()
