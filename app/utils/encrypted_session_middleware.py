from cryptography.fernet import Fernet
import json
import base64
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
import hmac
import hashlib


class EncryptedSessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        encryption_key: str,
        cookie_name: str = "session",
        max_age: int = 14 * 24 * 60 * 60,  # 14 days in seconds
        path: str = "/",
        same_site: str = "lax",
        secure: bool = False,
        domain: str = None,
    ):
        self.app = app
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.same_site = same_site
        self.secure = secure
        self.domain = domain
        self.secret_key = (
            secret_key.encode() if isinstance(secret_key, str) else secret_key
        )

        # Create a Fernet key from any string/bytes
        self.fernet = self._initialize_fernet(encryption_key)

    def _initialize_fernet(self, key):
        """Create a valid Fernet key from any input."""
        # Convert to bytes if needed
        if isinstance(key, str):
            key = key.encode()

        # Ensure key is 32 bytes (pad if needed)
        key = key.ljust(32)[:32]

        # Create valid base64 encoded key
        fernet_key = base64.urlsafe_b64encode(key)
        return Fernet(fernet_key)

    def _sign_data(self, data):
        """Create an HMAC signature using the secret key."""
        signature = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature)

    def _verify_signature(self, data, signature):
        """Verify the HMAC signature."""
        expected = self._sign_data(data)
        decoded_sig = base64.urlsafe_b64decode(signature)
        return hmac.compare_digest(expected, signature)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Initialize session data
        request = Request(scope)
        session_data = {}

        # Try to load session from cookie
        session_cookie = request.cookies.get(self.cookie_name)
        if session_cookie:
            try:
                # Split signature and data
                parts = session_cookie.split(".")
                if len(parts) == 2:
                    signature, data = parts

                    # Verify signature
                    if hmac.compare_digest(
                        self._sign_data(data.encode()), signature.encode()
                    ):
                        # Decrypt the data
                        decrypted = self.fernet.decrypt(data.encode(), ttl=self.max_age)
                        session_data = json.loads(decrypted.decode())
            except Exception:
                # Use empty session if anything fails
                session_data = {}

        # Store session in scope
        scope["session"] = session_data.copy()

        # Wrap send to add cookie if session is modified
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Check if session was modified
                if scope["session"] != session_data:
                    # Encrypt session data
                    serialized = json.dumps(scope["session"]).encode()
                    encrypted = self.fernet.encrypt(serialized)

                    # Create signature
                    signature = self._sign_data(encrypted)

                    # Create cookie value
                    cookie_value = f"{signature.decode()}.{encrypted.decode()}"

                    # Add cookie header
                    headers = MutableHeaders(scope=message)
                    cookie = f"{self.cookie_name}={cookie_value}; Path={self.path}"

                    if self.max_age:
                        cookie += f"; Max-Age={self.max_age}"
                    if self.domain:
                        cookie += f"; Domain={self.domain}"
                    if self.secure:
                        cookie += "; Secure"
                    if self.same_site:
                        cookie += f"; SameSite={self.same_site}"

                    cookie += "; HttpOnly"
                    headers.append("Set-Cookie", cookie)

            await send(message)

        await self.app(scope, receive, send_wrapper)
