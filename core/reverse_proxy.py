"""Reverse proxy handler — forward requests to upstream servers."""

import http.client
from urllib.parse import urlparse
from .response import Response


class ReverseProxy:
    """Forward requests to upstream backend servers."""

    def __init__(self, upstreams, prefix="/api"):
        """
        Args:
            upstreams: list of upstream URLs, e.g. ["http://localhost:3000"]
            prefix: URL prefix to proxy
        """
        self.upstreams = upstreams
        self.prefix = prefix.rstrip("/")
        self._current = 0

    def register(self, server):
        """Register proxy route on the server."""
        server.router.add_route("GET", f"{self.prefix}/*path", self._handle)
        server.router.add_route("POST", f"{self.prefix}/*path", self._handle)
        server.router.add_route("PUT", f"{self.prefix}/*path", self._handle)
        server.router.add_route("DELETE", f"{self.prefix}/*path", self._handle)

    def _get_upstream(self):
        """Round-robin upstream selection."""
        upstream = self.upstreams[self._current % len(self.upstreams)]
        self._current += 1
        return upstream

    def _handle(self, request, response):
        """Forward request to upstream server."""
        upstream_url = self._get_upstream()
        parsed = urlparse(upstream_url)
        path = "/" + request.params.get("path", "")

        try:
            if parsed.scheme == "https":
                conn = http.client.HTTPSConnection(parsed.hostname, parsed.port or 443, timeout=30)
            else:
                conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=30)

            # Forward headers
            forward_headers = {}
            for key, value in request.headers.items():
                if key.lower() not in ("host", "connection"):
                    forward_headers[key] = value
            forward_headers["Host"] = parsed.hostname
            forward_headers["X-Forwarded-For"] = request.client_ip
            forward_headers["X-Forwarded-Proto"] = "http"

            conn.request(
                request.method,
                path + (f"?{request.query_string}" if request.query_string else ""),
                body=request.body if request.body else None,
                headers=forward_headers,
            )

            upstream_resp = conn.getresponse()
            body = upstream_resp.read()

            response.status = upstream_resp.status
            response._body = body
            for key, value in upstream_resp.getheaders():
                if key.lower() not in ("transfer-encoding", "connection"):
                    response.set_header(key, value)
            response.set_header("X-Proxied-By", "PyServe")

            conn.close()
            return response

        except Exception as e:
            return Response(status=502, body=f"Bad Gateway: {e}")
