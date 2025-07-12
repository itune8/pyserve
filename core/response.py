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

    def redirect(self, url, permanent=False):
        """Send redirect response."""
        self.status = 301 if permanent else 302
        self.headers["Location"] = url
        self._body = b""
        return self

    def send_file(self, filepath):
        """Send a file as response."""
        if not os.path.isfile(filepath):
            self.status = 404
            self._body = b"File not found"
            return self

        mime, _ = mimetypes.guess_type(filepath)
        self.headers["Content-Type"] = mime or "application/octet-stream"

        with open(filepath, "rb") as f:
            self._body = f.read()

        self.headers["Content-Length"] = str(len(self._body))
        return self

    def set_cookie(self, name, value, max_age=None, path="/", httponly=True, secure=False):
        """Set a cookie."""
        cookie = f"{name}={value}; Path={path}"
        if max_age is not None:
            cookie += f"; Max-Age={max_age}"
        if httponly:
            cookie += "; HttpOnly"
        if secure:
            cookie += "; Secure"
        self.headers["Set-Cookie"] = cookie
        return self

    def build(self):
        """Build the raw HTTP response bytes."""
        status_msg = STATUS_MESSAGES.get(self.status, "Unknown")
        self.headers["Content-Length"] = str(len(self._body))

        lines = [f"HTTP/1.1 {self.status} {status_msg}"]
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")

        header_bytes = "\r\n".join(lines).encode("utf-8") + b"\r\n"
        return header_bytes + self._body
