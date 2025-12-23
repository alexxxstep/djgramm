# Django settings for DJGramm project

import os
import sys
from pathlib import Path

# Cloudinary settings
import cloudinary
import cloudinary.api
import cloudinary.uploader
import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")

# ALLOWED_HOSTS - ensure localhost and 127.0.0.1 are always included for health checks
_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(
    ","
)
# Strip whitespace and ensure localhost and 127.0.0.1 are always included
_allowed_hosts = [h.strip() for h in _allowed_hosts if h.strip()]
if "localhost" not in _allowed_hosts:
    _allowed_hosts.append("localhost")
if "127.0.0.1" not in _allowed_hosts:
    _allowed_hosts.append("127.0.0.1")
ALLOWED_HOSTS = _allowed_hosts

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Cloudinary
    "cloudinary",
    "cloudinary_storage",
    # Social Auth
    "social_django",
    # Local apps
    "app.apps.DjgrammAppConfig",
]

MIDDLEWARE = [
    "app.middleware.HealthCheckMiddleware",  # Must be BEFORE SecurityMiddleware
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise middleware - only in DEBUG mode (nginx serves static files in production)
    *(["whitenoise.middleware.WhiteNoiseMiddleware"] if DEBUG else []),
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Django Debug Toolbar Configuration (тільки для DEBUG)
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
    # Для Docker
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

    # Additional settings for Debug Toolbar
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_COLLAPSED": True,
    }

    # Settings for SQL Panel
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.history.HistoryPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        # "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]

# WhiteNoise settings for serving static files
WHITENOISE_USE_FINDERS = (
    True  # Allow WhiteNoise to serve static files in DEBUG mode
)

# WhiteNoise cache settings for static files
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files


def whitenoise_immutable_file_test(path, url):
    """Test if a file should be cached as immutable."""
    return url.startswith("/static/dist/")


WHITENOISE_IMMUTABLE_FILE_TEST = whitenoise_immutable_file_test

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "app.context_processors.unread_news_count",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    # PostgreSQL for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "djgramm"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

# Custom user model
AUTH_USER_MODEL = "app.User"

# Authentication backends
AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

# Social Auth settings
SOCIAL_AUTH_USER_MODEL = "app.User"

# OAuth redirect URLs
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/login/?error=oauth"
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = "/"
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = "/"

# GitHub OAuth settings
SOCIAL_AUTH_GITHUB_KEY = os.environ.get("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get("SOCIAL_AUTH_GITHUB_SECRET")
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email", "read:user"]

# Google OAuth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", ""
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", ""
)
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Pipeline settings (customized)
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "app.pipeline.associate_by_email",  # Custom: associate by email
    "app.pipeline.get_username",  # Custom: handle username conflicts
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "app.pipeline.create_profile",  # Custom: ensure Profile exists
    "app.pipeline.save_avatar",  # Custom: save avatar from OAuth
)

# Session security for OAuth
SOCIAL_AUTH_SANITIZE_REDIRECTS = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = not DEBUG


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = "/static/"
# Frontend built files are in frontend/dist
# In Docker: BASE_DIR = /app, frontend is at /app/frontend/dist
# On host: BASE_DIR = src/, frontend is at project root/frontend/dist
frontend_dist = BASE_DIR / "frontend" / "dist"
# Fallback to parent path if not found (host development case)
if not frontend_dist.exists():
    frontend_dist = BASE_DIR.parent / "frontend" / "dist"
# Only add to STATICFILES_DIRS if it exists
STATICFILES_DIRS = [frontend_dist] if frontend_dist.exists() else []
# Add static directory for app-level static files (favicon, etc.)
static_dir = BASE_DIR / "static"
if static_dir.exists():
    STATICFILES_DIRS = list(STATICFILES_DIRS) + [static_dir]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration
# Disabled when nginx serves static files (production with nginx)
# Enable only if Django serves static files directly (without nginx)
# if not DEBUG:
#     STATICFILES_STORAGE = (
#         "whitenoise.storage.CompressedManifestStaticFilesStorage"
#     )

# =============================================================================
# Media files
# =============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# Cloudinary Configuration
# =============================================================================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET", ""),
}

# Use Cloudinary for media files (only if credentials are provided)
cloud_name = CLOUDINARY_STORAGE["CLOUD_NAME"]
api_key = CLOUDINARY_STORAGE["API_KEY"]
api_secret = CLOUDINARY_STORAGE["API_SECRET"]

if cloud_name and api_key and api_secret:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
    )
else:
    # When Cloudinary credentials are not provided:
    # - Don't set DEFAULT_FILE_STORAGE (uses Django's default local storage)
    # - CloudinaryField will use local storage for new uploads
    # - However, if database contains public_id from previous Cloudinary uploads,
    #   CloudinaryField may still try to generate Cloudinary URLs
    # - Solution: Configure Cloudinary with empty values to prevent errors,
    #   but CloudinaryField should use local storage when DEFAULT_FILE_STORAGE
    #   is not set to MediaCloudinaryStorage
    # - For existing public_id values, they will try to use Cloudinary URLs
    #   which won't work. Consider migrating data or using real Cloudinary credentials.
    pass

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login/Logout redirects
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/login/"

# =============================================================================
# Production Security Settings
# =============================================================================
# Check if running tests (pytest sets this automatically)
TESTING = (
    "pytest" in sys.modules
    or "test" in sys.argv
    or os.environ.get("TESTING") == "True"
)

if not DEBUG and not TESTING:
    # HTTPS settings
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = (
        os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Other security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"
