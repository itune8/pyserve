"""URL router with pattern matching and path parameters."""

import re


class Router:
    """HTTP request router with dynamic path parameters."""

    def __init__(self):
        self._routes = {}  # {method: [(pattern, param_names, handler), ...]}

    def add_route(self, method, path, handler):
        """Register a route handler."""
        method = method.upper()
        if method not in self._routes:
            self._routes[method] = []

        pattern, param_names = self._compile_pattern(path)
        self._routes[method].append((pattern, param_names, handler))

    def match(self, method, path):
        """Find a matching route handler.

        Returns (handler, params) or (None, {}).
        """
        method = method.upper()
        routes = self._routes.get(method, [])

        for pattern, param_names, handler in routes:
            m = pattern.match(path)
            if m:
                params = dict(zip(param_names, m.groups()))
                return handler, params

        return None, {}

    def route_count(self):
        """Count total registered routes."""
        return sum(len(routes) for routes in self._routes.values())

    def list_routes(self):
        """List all registered routes."""
        result = []
        for method, routes in self._routes.items():
            for pattern, params, handler in routes:
                result.append({
                    "method": method,
                    "pattern": pattern.pattern,
                    "params": params,
                    "handler": handler.__name__,
                })
        return result

