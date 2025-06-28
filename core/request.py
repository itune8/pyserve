"""HTTP request parser."""

import json
from urllib.parse import urlparse, parse_qs


class Request:
    """Parsed HTTP request."""

    def __init__(self):
        self.method = "GET"
        self.path = "/"
        self.query_string = ""
        self.query = {}
        self.headers = {}
        self.body = b""
        self.client_ip = ""
        self.params = {}
        self.http_version = "HTTP/1.1"

    @classmethod
    def parse(cls, raw_data, addr=None):
        """Parse raw HTTP request bytes into a Request object."""
        req = cls()

        if addr:
            req.client_ip = addr[0]

        try:
            header_end = raw_data.index(b"\r\n\r\n")
            header_section = raw_data[:header_end].decode("utf-8")
            req.body = raw_data[header_end + 4:]
        except (ValueError, UnicodeDecodeError):
            return req

        lines = header_section.split("\r\n")
        if not lines:
            return req

        # Request line: GET /path HTTP/1.1
        parts = lines[0].split(" ", 2)
        if len(parts) >= 2:
            req.method = parts[0].upper()
            parsed = urlparse(parts[1])
            req.path = parsed.path or "/"
            req.query_string = parsed.query
            req.query = {k: v[0] if len(v) == 1 else v
                         for k, v in parse_qs(parsed.query).items()}
        if len(parts) >= 3:
            req.http_version = parts[2]

        # Headers
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                req.headers[key.strip().lower()] = value.strip()

        return req

