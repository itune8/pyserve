# PyServe

Lightweight HTTP web server framework built from scratch in Python using raw sockets. Features routing, middleware, static file serving, reverse proxy, and authentication.

## Features

- **HTTP Server** — Multithreaded server built on raw sockets (no Flask/Django)
- **Router** — Pattern matching with path parameters (`:id`) and wildcards (`*path`)
- **Middleware Stack** — Chainable middleware: logging, CORS, rate limiting, compression, auth
- **Static File Serving** — Serve files with MIME detection and directory traversal protection
- **Reverse Proxy** — Forward requests to upstream servers with round-robin load balancing
- **Response Builder** — JSON, HTML, text, file, redirect, cookies
- **Authentication** — API key and HTTP Basic auth middleware
- **Rate Limiting** — Token bucket algorithm per client IP
- **Gzip Compression** — Automatic response compression

## Quick Start

```bash
# Run the example app
python app.py

# Server starts on http://localhost:8080
```

## API

```python
from core.server import HTTPServer

app = HTTPServer(host="0.0.0.0", port=8080)

@app.get("/")
def index(req, res):
    return res.html("<h1>Hello World</h1>")

@app.get("/api/users/:id")
def get_user(req, res):
    user_id = req.params["id"]
    return res.json({"id": user_id})

@app.post("/api/data")
def create(req, res):
    data = req.json()
    return res.json({"received": data}, status=201)

app.start()
```

## Project Structure

```
pyserve/
├── app.py                       # Example application
├── core/
│   ├── server.py                # HTTP server engine
│   ├── request.py               # Request parser
│   ├── response.py              # Response builder
│   ├── router.py                # URL router with params
│   ├── static.py                # Static file handler
│   └── reverse_proxy.py         # Reverse proxy with load balancing
├── middleware/
│   ├── logger.py                # Request logging
│   ├── cors.py                  # CORS headers
│   ├── rate_limiter.py          # Token bucket rate limiter
│   ├── auth.py                  # API key & Basic auth
│   └── compression.py           # Gzip compression
├── static/                      # Static files directory
├── tests/
│   └── test_server.py           # Unit tests
└── README.md
```
