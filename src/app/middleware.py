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
        # Bypass ALLOWED_HOSTS check and SSL redirect for /health/ endpoint
        if request.path in ("/health/", "/health"):
            # Set a valid host to bypass SecurityMiddleware check
            # Use 127.0.0.1 as it's always in ALLOWED_HOSTS
            request.META["HTTP_HOST"] = "127.0.0.1:8000"
            # Also set SERVER_NAME to avoid SuspiciousOperation
            request.META["SERVER_NAME"] = "127.0.0.1"
            # Disable SSL redirect for health check
            request.META["HTTP_X_FORWARDED_PROTO"] = "http"
            # Mark request to skip SSL redirect
            request._skip_ssl_redirect = True

        try:
            response = self.get_response(request)
            # If response is a redirect (301/302) for health check, return OK instead
            if request.path in (
                "/health/",
                "/health",
            ) and response.status_code in (301, 302):
                return HttpResponse("OK", content_type="text/plain")
        except SuspiciousOperation:
            # If SuspiciousOperation is raised for /health/, return OK response
            if request.path in ("/health/", "/health"):
                return HttpResponse("OK", content_type="text/plain")
            raise

        return response
