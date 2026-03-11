from typing import Optional
from fastapi import Request


def extract_bearer_token(request: Request) -> Optional[str]:
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return None

    scheme, _, token = authorization_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()
