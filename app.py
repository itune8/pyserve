"""Example application using PyServe."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.server import HTTPServer
from core.static import StaticFileHandler
from middleware.logger import logger_middleware
from middleware.cors import cors_middleware
from middleware.rate_limiter import rate_limiter

app = HTTPServer(host="0.0.0.0", port=8080)

# ── Middleware ────────────────────────────────────────────────────

app.use(logger_middleware)
app.use(cors_middleware())
app.use(rate_limiter(requests_per_second=50, burst=100))

# ── Static files ─────────────────────────────────────────────────

static_dir = os.path.join(os.path.dirname(__file__), "static")
StaticFileHandler(static_dir, prefix="/static").register(app)

# ── Routes ───────────────────────────────────────────────────────

@app.get("/")
def index(req, res):
    return res.html("""
    <html>
    <head><title>PyServe</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 700px; margin: 4rem auto; padding: 0 1rem; color: #333; }
        h1 { color: #2c3e50; } code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        .endpoint { margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-left: 3px solid #3498db; }
    </style></head>
    <body>
        <h1>PyServe</h1>
        <p>Lightweight HTTP web server framework built from scratch in Python.</p>
        <h3>API Endpoints</h3>
        <div class="endpoint"><code>GET /</code> — This page</div>
        <div class="endpoint"><code>GET /health</code> — Health check</div>
        <div class="endpoint"><code>GET /api/info</code> — Server info</div>
        <div class="endpoint"><code>GET /api/routes</code> — List routes</div>
        <div class="endpoint"><code>GET /api/users/:id</code> — Get user by ID</div>
        <div class="endpoint"><code>POST /api/echo</code> — Echo request body</div>
        <div class="endpoint"><code>GET /static/*</code> — Static files</div>
    </body></html>
    """)


@app.get("/health")
def health(req, res):
    return res.json({"status": "healthy", "server": "PyServe/1.0"})


@app.get("/api/info")
def server_info(req, res):
    import platform
    return res.json({
        "server": "PyServe/1.0",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "host": f"{app.host}:{app.port}",
        "workers": app.workers,
        "routes": app.router.route_count(),
    })


@app.get("/api/routes")
def list_routes(req, res):
    return res.json(app.router.list_routes())


