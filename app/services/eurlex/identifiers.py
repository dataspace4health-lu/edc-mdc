"""
Utilities for converting between ELI and CELEX identifiers.

ELI (European Legislation Identifier) is a standard URI format for EU legislation.
CELEX is the internal identifier system used by EUR-Lex.
"""

from __future__ import annotations
import re


def extract_celex_from_input(filter: str) -> str | None:
    """
    Extract CELEX identifier from various input formats.

    Supports:
    - Full URL: https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:51991IP0963
    - CELEX URI: CELEX:51991IP0963
    - Raw CELEX: 51991IP0963

    Returns the CELEX number or None if not found.
    """
    # Check if it's a EUR-Lex URL
    celex_url_pattern = r"eur-lex\.europa\.eu.*[?&]uri=CELEX:([A-Z0-9]+)"
    match = re.search(celex_url_pattern, filter, re.IGNORECASE)
    if match:
        return match.group(1)

    # Check if it's a CELEX URI format (CELEX:51991IP0963)
    celex_uri_pattern = r"(?:^|[^/])CELEX:([A-Z0-9]+)"
    match = re.search(celex_uri_pattern, filter, re.IGNORECASE)
    if match:
        return match.group(1)

    # Check if it looks like a raw CELEX identifier (e.g., 51991IP0963)
    # CELEX format: typically starts with digit, contains letters and digits
    celex_raw_pattern = r"^[0-9]{1,2}[0-9]{4}[A-Z]{1,2}[0-9]{4}[A-Z]?$"
    if re.match(celex_raw_pattern, filter, re.IGNORECASE):
        return filter.upper()

    return None


def convert_eli_to_celex(eli_type: str, year: str, number: str) -> str | None:
    """
    Convert ELI components to CELEX identifier.

    ELI format: /eli/{type}/{year}/{number}/{version}
    CELEX format: {sector}{year}{type_letter}{number}

    Examples:
    - eli/dir/2007/60 -> 32007L0060 (directive)
    - eli/reg/2018/1725 -> 32018R1725 (regulation)
    - eli/dec/2019/456 -> 32019D0456 (decision)
    """
    # Map ELI type to CELEX type letter and sector
    eli_to_celex_map = {
        "dir": ("L", "3"),  # Directive
        "reg": ("R", "3"),  # Regulation
        "dec": ("D", "3"),  # Decision
        "dec_impl": ("D", "3"),  # Implementing Decision
        "rec": ("H", "3"),  # Recommendation
    }

    eli_type_lower = eli_type.lower()
    if eli_type_lower not in eli_to_celex_map:
        return None

    type_letter, sector = eli_to_celex_map[eli_type_lower]

    # Pad number to 4 digits
    try:
        num_padded = str(int(number)).zfill(4)
    except ValueError:
        return None

    # Build CELEX: {sector}{year}{type_letter}{number}
    celex = f"{sector}{year}{type_letter}{num_padded}"
    return celex


def extract_eli_from_input(filter: str) -> str | None:
    """
    Extract and convert ELI identifier from various input formats to CELEX.

    Supports:
    - ELI URL: https://eur-lex.europa.eu/eli/dir/2007/60/oj
    - ELI URL: http://data.europa.eu/eli/dir/2007/60/oj
    - ELI path: eli/dir/2007/60/oj

    Returns the CELEX number or None if not found/convertible.
    """
    # Pattern to match ELI format: eli/{type}/{year}/{number}
    # The version (oj, etc.) and locale params are optional
    eli_pattern = r"eli/([a-z_]+)/(\d{4})/(\d+)"
    match = re.search(eli_pattern, filter, re.IGNORECASE)
    if match:
        eli_type = match.group(1)
        year = match.group(2)
        number = match.group(3)
        return convert_eli_to_celex(eli_type, year, number)

    return None
