"""Tests for PyServe components."""

import sys
import os
import unittest
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.request import Request
from core.response import Response
from core.router import Router
from core.static import StaticFileHandler


class TestRequest(unittest.TestCase):
    def test_parse_get(self):
        raw = b"GET /hello?name=world HTTP/1.1\r\nHost: localhost\r\n\r\n"
        req = Request.parse(raw, ("127.0.0.1", 8080))
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.path, "/hello")
        self.assertEqual(req.query, {"name": "world"})
        self.assertEqual(req.client_ip, "127.0.0.1")

    def test_parse_post_json(self):
        body = json.dumps({"key": "value"})
        raw = f"POST /api HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
        req = Request.parse(raw)
        self.assertEqual(req.method, "POST")
        self.assertTrue(req.is_json)
        self.assertEqual(req.json(), {"key": "value"})

    def test_parse_headers(self):
        raw = b"GET / HTTP/1.1\r\nHost: localhost\r\nX-Custom: test\r\n\r\n"
        req = Request.parse(raw)
        self.assertEqual(req.get_header("host"), "localhost")
        self.assertEqual(req.get_header("x-custom"), "test")
        self.assertIsNone(req.get_header("missing"))

    def test_empty_request(self):
        req = Request.parse(b"")
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.path, "/")


class TestResponse(unittest.TestCase):
    def test_json_response(self):
        res = Response()
        res.json({"hello": "world"})
        raw = res.build()
        self.assertIn(b"200 OK", raw)
        self.assertIn(b"application/json", raw)
        self.assertIn(b'"hello"', raw)

    def test_html_response(self):
        res = Response()
        res.html("<h1>Hello</h1>")
        raw = res.build()
        self.assertIn(b"text/html", raw)
        self.assertIn(b"<h1>Hello</h1>", raw)

    def test_status_codes(self):
        res = Response(status=404, body="Not Found")
        raw = res.build()
        self.assertIn(b"404 Not Found", raw)

    def test_redirect(self):
        res = Response()
        res.redirect("/new-location")
        raw = res.build()
        self.assertIn(b"302 Found", raw)
        self.assertIn(b"Location: /new-location", raw)

    def test_set_cookie(self):
        res = Response()
        res.set_cookie("session", "abc123", max_age=3600)
        raw = res.build()
        self.assertIn(b"Set-Cookie: session=abc123", raw)
        self.assertIn(b"Max-Age=3600", raw)
        self.assertIn(b"HttpOnly", raw)

    def test_set_header(self):
        res = Response()
        res.set_header("X-Custom", "value")
        raw = res.build()
        self.assertIn(b"X-Custom: value", raw)

    def test_send_file(self):
        tmpfile = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w")
        tmpfile.write("file content")
        tmpfile.close()
 