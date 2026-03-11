import jwt
from typing import Optional
from services.user import UserService
from services.config import ConfigService
from auth.session_auth import extract_iam_roles


def create_or_find_service_account_user(
    user_service: UserService,
    access_token: str,
    service_account_client_id: str,
    config_service: Optional[ConfigService] = None,
    display_name: Optional[str] = None,
) -> int:
    # Decode JWT without verification to extract claims
    # We already trust this token since we obtained it from the OIDC provider
    decoded = jwt.decode(access_token, options={"verify_signature": False})

    sub = decoded.get("sub")
    if not sub:
        raise ValueError("Missing 'sub' claim in service account token")

    # Extract IAM roles from JWT token if config_service is provided
    iam_roles = []
    if config_service:
        iam_roles = extract_iam_roles(config_service, decoded, validate_roles=False)

    # Use provided display name or default to technical name
    name = display_name or f"Service Account ({service_account_client_id})"

    # Create or find user for this service account
    # This ensures each service account has its own user with its own roles
    user = user_service.create_or_find(
        email=None,  # Service accounts don't have email
        name=name,
        external_id=sub,
        iam_roles=iam_roles,
    )

    return user.id
