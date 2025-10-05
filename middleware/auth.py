"""Authentication middleware — API key and Basic auth."""

import base64
import hashlib
import hmac
from core.response import Response


def api_key_auth(valid_keys, header_name="X-API-Key"):
    """API key authentication middleware."""
    key_set = set(valid_keys) if isinstance(valid_keys, list) else {valid_keys}

    def middleware(request, response, next_handler):
        api_key = request.get_header(header_name)
        if not api_key or api_key not in key_set:
            return Response(status=401).json({"error": "Invalid or missing API key"}, 401)
        return next_handler(request, response)

    return middleware


def basic_auth(credentials):
    """HTTP Basic authentication middleware.

    Args:
        credentials: dict of {username: password}
    """
    def middleware(request, response, next_handler):
        auth_header = request.get_header("authorization", "")
        if not auth_header.startswith("Basic "):
            resp = Response(status=401, body="Authentication required")
            resp.set_header("WWW-Authenticate", 'Basic realm="PyServe"')
            return resp

        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            return Response(status=401, body="Invalid credentials")

        if username not in credentials or not hmac.compare_digest(
            credentials[username], password
        ):
            return Response(status=401, body="Invalid credentials")

        request.user = username
        return next_handler(request, response)

    return middleware

