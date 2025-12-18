"""Custom middleware for DJGramm app."""

from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse


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
            # Use 127.0.0.1 as it's always in ALLOWED_HOSTS
            request.META["HTTP_HOST"] = "127.0.0.1:8000"
            # Also set SERVER_NAME to avoid SuspiciousOperation
            request.META["SERVER_NAME"] = "127.0.0.1"

        try:
            response = self.get_response(request)
        except SuspiciousOperation:
            # If SuspiciousOperation is raised for /health/, return OK response
            if request.path == "/health/":
                return HttpResponse("OK", content_type="text/plain")
            raise

        return response
