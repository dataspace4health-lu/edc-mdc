import os
import ssl
from authlib.integrations.starlette_client import OAuth
from jwt import PyJWKClient
import jwt

# Initialize OAuth client
oauth = OAuth()
oauth.register(
    name="oidc",
    client_id=os.getenv("OPENID_CLIENT_ID"),
    client_secret=os.getenv("OPENID_CLIENT_SECRET"),
    authorize_url=os.getenv("OPENID_AUTH_URL"),
    access_token_url=os.getenv("OPENID_TOKEN_URL"),
    jwks_uri=os.getenv("OPENID_JWKS_URL"),
    client_kwargs={
        "verify": (
            False
            if os.getenv("OPENID_VERIFY", "False") == "False"
            else os.getenv("OPENID_VERIFY")
        ),
        "scope": "openid email profile",
        "code_challenge_method": "S256",
    },
)

# Initialize JWKS client for JWT verification
# Use unverified SSL context if OPENID_VERIFY is False
_openid_verify = os.getenv("OPENID_VERIFY", "False") == "True"
_ssl_context = None if _openid_verify else ssl._create_unverified_context()
jwks_client = PyJWKClient(os.getenv("OPENID_JWKS_URL"), ssl_context=_ssl_context)


async def authorize_access_token(request):
    token = await oauth.oidc.authorize_access_token(request)

    # Try to get userinfo from the token response first (most reliable)
    if "userinfo" in token:
        return token["userinfo"]

    # Fallback: try to decode ID token if available
    id_token = token.get("id_token")
    if id_token:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        return jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=os.getenv("OPENID_CLIENT_ID"),
            options={"verify_exp": True, "verify_iat": False},
        )

    # Last resort: try access token (for non-standard providers)
    access_token = token.get("access_token")
    if access_token:
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(access_token)
            return jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=os.getenv("OPENID_CLIENT_ID"),
                options={"verify_exp": True, "verify_iat": False},
            )
        except Exception:
            # If access token decoding fails, make userinfo request
            pass

    # If all else fails, make explicit userinfo request
    userinfo_response = await oauth.oidc.get_userinfo(token)
    return userinfo_response
