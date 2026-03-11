import re
from typing import Optional


def validate_temporal_resolution(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return value

    # ISO 8601 duration pattern (no negative values allowed)
    # Format: P[n]Y[n]M[n]W[n]DT[n]H[n]M[n]S
    # P is required, then any combination of:
    # - Y (years), M (months), W (weeks), D (days)
    # - T followed by H (hours), M (minutes), S (seconds with optional decimals)
    pattern = r"^P(?:\d+Y)?(?:\d+M)?(?:\d+W)?(?:\d+D)?(?:T(?:\d+H)?(?:\d+M)?(?:\d+(?:\.\d+)?S)?)?$"

    if not re.match(pattern, value):
        raise ValueError(
            "Temporal resolution must be in ISO 8601 duration format "
            "(e.g., P1D for daily, PT1H for hourly, P1M for monthly). "
            "Negative values are not allowed."
        )

    # Ensure it's not just "P" or "PT" (must have at least one component)
    if value in ["P", "PT"]:
        raise ValueError("Temporal resolution must specify at least one time component")

    return value
