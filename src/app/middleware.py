"""Custom middleware for DJGramm app."""


class HealthCheckMiddleware:
    """
    Middleware to bypass ALLOWED_HOSTS check for health check endpoint.
    This allows Docker healthchecks to work without configuring ALLOWED_HOSTS.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass ALLOWED_HOSTS check for /health/ endpoint
        if request.path == "/health/":
            # Set a valid host to bypass SecurityMiddleware check
            request.META["HTTP_HOST"] = "localhost"
            # Also set SERVER_NAME to avoid SuspiciousOperation
            if "SERVER_NAME" not in request.META:
                request.META["SERVER_NAME"] = "localhost"

        response = self.get_response(request)
        return response
