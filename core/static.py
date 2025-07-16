"""Static file serving handler."""

import os
import mimetypes
from .response import Response


class StaticFileHandler:
    """Serves static files from a directory."""

    def __init__(self, directory, prefix="/static"):
        self.directory = os.path.abspath(directory)
        self.prefix = prefix.rstrip("/")

    def register(self, server):
        """Register the static file route on the server."""
        pattern = f"{self.prefix}/*filepath"
        server.router.add_route("GET", pattern, self._handle)

    def _handle(self, request, response):
        filepath = request.params.get("filepath", "")

        # Prevent directory traversal
        safe_path = os.path.normpath(filepath)
        if safe_path.startswith("..") or safe_path.startswith("/"):
            return response.text("Forbidden", status=403)

        full_path = os.path.join(self.directory, safe_path)

        if not full_path.startswith(self.directory):
            return response.text("Forbidden", status=403)

        if os.path.isdir(full_path):
            index = os.path.join(full_path, "index.html")
            if os.path.isfile(index):
                full_path = index
            else:
                return response.text("Not Found", status=404)

        if not os.path.isfile(full_path):
            return response.text("Not Found", status=404)

        return response.send_file(full_path)
