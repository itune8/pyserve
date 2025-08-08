"""Response compression middleware."""

import gzip


def compression_middleware(min_size=1024):
    """Gzip compression for responses above min_size bytes."""

    def middleware(request, response, next_handler):
        result = next_handler(request, response)

        accept_encoding = request.get_header("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return result

        if not hasattr(result, '_body') or len(result._body) < min_size:
            return result

        content_type = result.headers.get("Content-Type", "")
        compressible = any(t in content_type for t in [
            "text/", "application/json", "application/javascript", "application/xml",
        ])

        if not compressible:
            return result

        compressed = gzip.compress(result._body)
        if len(compressed) < len(result._body):
            result._body = compressed
            result.set_header("Content-Encoding", "gzip")
            result.set_header("Content-Length", str(len(compressed)))

        return result

    return middleware
