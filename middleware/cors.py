"""CORS (Cross-Origin Resource Sharing) middleware."""


def cors_middleware(allowed_origins="*", allowed_methods=None, allowed_headers=None, max_age=86400):
    """Create a CORS middleware with configurable options."""
    if allowed_methods is None:
        allowed_methods = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    if allowed_headers is None:
        allowed_headers = "Content-Type, Authorization, X-Requested-With"

    def middleware(request, response, next_handler):
        result = next_handler(request, response)

        if hasattr(result, 'set_header'):
            result.set_header("Access-Control-Allow-Origin", allowed_origins)
            result.set_header("Access-Control-Allow-Methods", allowed_methods)
            result.set_header("Access-Control-Allow-Headers", allowed_headers)
            result.set_header("Access-Control-Max-Age", str(max_age))

        return result

    return middleware

