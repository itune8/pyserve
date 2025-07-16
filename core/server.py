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

    # ── Middleware ────────────────────────────────────────────────

    def use(self, middleware):
        """Register a middleware function.

        Middleware signature: middleware(request, response, next_handler) -> response
        """
        self._middlewares.append(middleware)
        return self

    def error_handler(self, handler):
        """Register a global error handler."""
        self._error_handler = handler
        return handler

    # ── Server lifecycle ─────────────────────────────────────────

    def start(self):
        """Start the HTTP server."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(self.workers * 2)
        self._socket.settimeout(1.0)
        self._running = True

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        print(f"[pyserve] Server running on http://{self.host}:{self.port}")
        print(f"[pyserve] Workers: {self.workers}")
        print(f"[pyserve] Routes: {self.router.route_count()}")
        print(f"[pyserve] Press Ctrl+C to stop\n")

        while self._running:
            try:
                client_sock, addr = self._socket.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, addr),
                    daemon=True,
                )
                thread.start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _shutdown(self, signum=None, frame=None):
        print("\n[pyserve] Shutting down...")
        self._running = False
        if self._socket:
            self._socket.close()

    def _handle_client(self, client_sock, addr):
        """Handle a single client connection."""
        try:
            client_sock.settimeout(30)
            raw_data = b""
            while True:
                chunk = client_sock.recv(4096)
                raw_data += chunk
                if len(chunk) < 4096 or b"\r\n\r\n" in raw_data:
                    break

            if not raw_data:
                return

            request = Request.parse(raw_data, addr)
            response = self._process_request(request)
            client_sock.sendall(response.build())

            self._log_request(request, response)
        except Exception as e:
            try:
                error_resp = Response(status=500, body=f"Internal Server Error: {e}")
                client_sock.sendall(error_resp.build())
            except Exception:
                pass
        finally:
            client_sock.close()

    def _process_request(self, request):
        """Process request through middleware chain and router."""
        try:
            handler, params = self.router.match(request.method, request.path)
            request.params = params

            if handler is None:
                return Response(status=404, body="404 Not Found")

            # Build middleware chain
            def final_handler(req, res):
                result = handler(req, res)
                if isinstance(result, Response):
                    return result
                return res

            chain = final_handler
            for mw in reversed(self._middlewares):
                prev = chain
                chain = lambda req, res, _mw=mw, _prev=prev: _mw(req, res, _prev)

            response = Response()
            result = chain(request, response)
            return result if isinstance(result, Response) else response

        except Exception as e:
            if self._error_handler:
                try:
                    return self._error_handler(request, e)
                except Exception:
                    pass
            return Response(status=500, body=f"Internal Server Error: {e}")

    def _log_request(self, request, response):
        """Log request to stdout."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = "\033[32m" if response.status < 400 else "\033[31m"
        reset = "\033[0m"
        print(f"  {color}{request.method} {request.path} -> {response.status}{reset} "
              f"[{timestamp}] {request.client_ip}")
