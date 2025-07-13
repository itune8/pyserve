"""Core HTTP server built on Python's socketserver."""

import socket
import threading
import signal
import sys
from datetime import datetime
from .request import Request
from .response import Response
from .router import Router


class HTTPServer:
    """Lightweight multithreaded HTTP server."""

    def __init__(self, host="0.0.0.0", port=8080, workers=4):
        self.host = host
        self.port = port
        self.workers = workers
        self.router = Router()
        self._middlewares = []
        self._running = False
        self._socket = None
        self._error_handler = None

    # ── Route registration ───────────────────────────────────────

    def route(self, path, methods=None):
        """Decorator to register a route handler."""
        if methods is None:
            methods = ["GET"]

        def decorator(handler):
            for method in methods:
                self.router.add_route(method.upper(), path, handler)
            return handler
        return decorator

    def get(self, path):
        return self.route(path, ["GET"])

    def post(self, path):
        return self.route(path, ["POST"])

    def put(self, path):
        return self.route(path, ["PUT"])

    def delete(self, path):
        return self.route(path, ["DELETE"])

