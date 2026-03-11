from __future__ import annotations
from typing import Any, Dict, Optional
import httpx
import os
import xml.etree.ElementTree as ET


class EurlexClient:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout_sec: float = 30.0,
    ) -> None:
        self.endpoint = endpoint or os.getenv(
            "EURLEX_ENDPOINT", "https://eur-lex.europa.eu/EURLexWebService"
        )
        self.username = username or os.getenv("EURLEX_USERNAME", "")
        self.password = password or os.getenv("EURLEX_PASSWORD", "")
        self.timeout = timeout_sec

    def _build_soap_request(
        self,
        expert_query: str,
        page: int = 1,
        page_size: int = 10,
        search_language: str = "en",
        exclude_all_consleg: bool = False,
        limit_to_latest_consleg: bool = False,
    ) -> str:
        """Build SOAP XML request for EUR-Lex web service"""
        soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:sear="http://eur-lex.europa.eu/search"
               xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Header>
        <wsse:Security soap:mustUnderstand="true"
                      xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <wsse:UsernameToken wsu:Id="UsernameToken-1"
                               xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
                <wsse:Username>{self.username}</wsse:Username>
                <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{self.password}</wsse:Password>
            </wsse:UsernameToken>
        </wsse:Security>
    </soap:Header>
    <soap:Body>
        <sear:searchRequest>
            <sear:expertQuery>{expert_query}</sear:expertQuery>
            <sear:page>{page}</sear:page>
            <sear:pageSize>{page_size}</sear:pageSize>
            <sear:searchLanguage>{search_language}</sear:searchLanguage>
            <sear:excludeAllConsleg>{str(exclude_all_consleg).lower()}</sear:excludeAllConsleg>
            <sear:limitToLatestConsleg>{str(limit_to_latest_consleg).lower()}</sear:limitToLatestConsleg>
        </sear:searchRequest>
    </soap:Body>
</soap:Envelope>"""
        return soap_request

    def _parse_soap_response(self, xml_response: str) -> Dict[str, Any]:
        """Parse SOAP XML response and extract search results"""
        try:
            root = ET.fromstring(xml_response)

            # Define namespaces
            namespaces = {
                "soap": "http://www.w3.org/2003/05/soap-envelope",
                "sear": "http://eur-lex.europa.eu/search",
            }

            # Extract search results
            results = []
            body = root.find(".//soap:Body", namespaces)
            if body is None:
                return {"results": [], "numhits": 0, "totalhits": 0}

            search_results = body.find(".//sear:searchResults", namespaces)
            if search_results is None:
                return {"results": [], "numhits": 0, "totalhits": 0}

            # Extract metadata
            numhits = search_results.findtext("sear:numhits", "0", namespaces)
            totalhits = search_results.findtext("sear:totalhits", "0", namespaces)

            # Extract individual results
            for result_elem in search_results.findall(".//sear:result", namespaces):
                reference = result_elem.findtext("sear:reference", "", namespaces)
                rank = result_elem.findtext("sear:rank", "", namespaces)

                # Extract content (metadata)
                content = {}
                content_elem = result_elem.find("sear:content", namespaces)
                title = None
                celex = None  # CELEX identifier for building URLs

                if content_elem is not None:
                    # Extract title and CELEX by iterating through elements
                    for elem in content_elem.iter():
                        # Extract title from EXPRESSION_TITLE
                        if elem.tag.endswith("EXPRESSION_TITLE") and not title:
                            for value_elem in elem.iter():
                                if value_elem.tag.endswith("VALUE") and value_elem.text:
                                    title = value_elem.text
                                    break
                        # Extract CELEX identifier from SAMEAS URIs
                        # Format: http://publications.europa.eu/resource/celex/31981R1653.ENG.pdfa1b
                        if (
                            not celex
                            and elem.tag.endswith("VALUE")
                            and elem.text
                            and "/celex/" in elem.text
                        ):
                            celex_uri = elem.text
                            # Extract CELEX number (e.g., 31981R1653)
                            celex_part = celex_uri.split("/celex/")[-1]
                            # Remove file extension and language suffix
                            celex = (
                                celex_part.split(".")[0]
                                if "." in celex_part
                                else celex_part
                            )

                    # Use defaults if not found
                    content["title"] = title or reference
                    if celex:
                        content["celex"] = celex

                # Extract document links
                links = []
                for link_elem in result_elem.findall(
                    ".//sear:document_link", namespaces
                ):
                    link_type = link_elem.findtext("sear:type", "", namespaces)
                    link_url = link_elem.findtext("sear:url", "", namespaces)
                    if link_url:
                        links.append({"type": link_type, "url": link_url})

                results.append(
                    {
                        "reference": reference,
                        "rank": rank,
                        "content": content,
                        "links": links,
                    }
                )

            return {
                "results": results,
                "numhits": int(numhits),
                "totalhits": int(totalhits),
            }

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML response: {e}")

    async def search(
        self,
        expert_query: str,
        page: int = 1,
        page_size: int = 10,
        search_language: str = "en",
        exclude_all_consleg: bool = False,
        limit_to_latest_consleg: bool = False,
    ) -> Dict[str, Any]:
        """Execute search query against EUR-Lex web service"""
        soap_request = self._build_soap_request(
            expert_query=expert_query,
            page=page,
            page_size=page_size,
            search_language=search_language,
            exclude_all_consleg=exclude_all_consleg,
            limit_to_latest_consleg=limit_to_latest_consleg,
        )

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Accept": "application/soap+xml",
            "SOAPAction": "https://eur-lex.europa.eu/EURLexWebService/doQuery",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=False
        ) as client:
            resp = await client.post(
                self.endpoint, content=soap_request, headers=headers
            )

            # Handle redirects - EUR-Lex sometimes redirects when service is unavailable
            if resp.status_code in (301, 302, 307, 308):
                raise httpx.HTTPStatusError(
                    f"EUR-Lex web service is temporarily unavailable (redirected to {resp.headers.get('location', 'unknown')})",
                    request=resp.request,
                    response=resp,
                )

            resp.raise_for_status()
            return self._parse_soap_response(resp.text)
