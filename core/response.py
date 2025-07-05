"""HTTP response builder."""

import json
import os
import mimetypes
from datetime import datetime

STATUS_MESSAGES = {
    200: "OK", 201: "Created", 204: "No Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
    404: "Not Found", 405: "Method Not Allowed",
    500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable",
}


class Response:
    """HTTP response builder with chainable methods."""

    def __init__(self, status=200, body="", content_type="text/plain"):
        self.status = status
        self._body = body.encode("utf-8") if isinstance(body, str) else body
        self.headers = {
            "Content-Type": content_type,
            "Server": "PyServe/1.0",
            "Date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "Connection": "close",
        }

    def set_status(self, code):
        self.status = code
        return self

    def set_header(self, key, value):
        self.headers[key] = value
        return self

    def json(self, data, status=200):
        """Send JSON response."""
        self.status = status
        self._body = json.dumps(data).encode("utf-8")
        self.headers["Content-Type"] = "application/json"
        return self

    def html(self, content, status=200):
        """Send HTML response."""
        self.status = status
        self._body = content.encode("utf-8") if isinstance(content, str) else content
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        return self

    def text(self, content, status=200):
        """Send plain text response."""
        self.status = status
        self._body = content.encode("utf-8") if isinstance(content, str) else content
        self.headers["Content-Type"] = "text/plain; charset=utf-8"
        return self

