"""Rate limiting middleware using token bucket algorithm."""

import time
import threading
from core.response import Response


class TokenBucket:
    """Thread-safe token bucket for rate limiting."""

    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


def rate_limiter(requests_per_second=10, burst=20):
    """Create a rate limiting middleware."""
    buckets = {}
    lock = threading.Lock()

    def middleware(request, response, next_handler):
        client_ip = request.client_ip

        with lock:
            if client_ip not in buckets:
                buckets[client_ip] = TokenBucket(requests_per_second, burst)

        bucket = buckets[client_ip]
        if not bucket.consume():
            return Response(status=429, body="Rate limit exceeded. Try again later.")

        result = next_handler(request, response)

        if hasattr(result, 'set_header'):
            result.set_header("X-RateLimit-Limit", str(burst))

        return result

    return middleware

