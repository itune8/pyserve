"""Request logging middleware."""

import time


def logger_middleware(request, response, next_handler):
    """Log request timing and details."""
    start = time.time()
    result = next_handler(request, response)
    elapsed = (time.time() - start) * 1000

    if hasattr(result, 'set_header'):
        result.set_header("X-Response-Time", f"{elapsed:.2f}ms")

    return result

