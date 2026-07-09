import os
import cloudinary
import dj_database_url

# Import all common settings from settings.py
from .settings import *

# ==========================================================
# SECURITY SETTINGS
# ==========================================================

# Disable debug mode in production.
# Never enable DEBUG=True on a public server.
DEBUG = False

# Secret key used for cryptographic signing (sessions, CSRF, etc.)
# Stored in Render environment variables.
SECRET_KEY = os.environ.get("SECRET_KEY")

# Render automatically provides your application's hostname.
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

# Domains allowed to serve this Django application.
# Prevents Host Header attacks.
ALLOWED_HOSTS = [
    RENDER_HOSTNAME,
    ".onrender.com",
]

# Allowed domains for CSRF protection.
# Required when your frontend submits POST/PUT/DELETE requests.
CSRF_TRUSTED_ORIGINS = [
    f"https://{RENDER_HOSTNAME}",
]

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DATABASES = {
    "default": dj_database_url.config(

        # PostgreSQL connection URL from Render environment variable.
        default=os.environ.get("DATABASE_URL"),

        # Reuse database connections for 60 seconds.
        # Reduces connection overhead while avoiding stale connections.
        conn_max_age=60,

        # Before reusing an old connection, Django checks whether
        # the connection is still alive.
        # Prevents "server closed the connection unexpectedly".
        conn_health_checks=True,

        # Force SSL connection between Render and Supabase.
        ssl_require=True,
    )
}

# Database connection timeout.
# If database doesn't respond within 30 seconds,
# Django raises an exception instead of hanging forever.
DATABASES["default"]["OPTIONS"] = {
    "connect_timeout": 30,
}

# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [

    # Security headers.
    "django.middleware.security.SecurityMiddleware",

    # Serve static files efficiently.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Session support.
    "django.contrib.sessions.middleware.SessionMiddleware",

    # Enable CORS.
    "corsheaders.middleware.CorsMiddleware",

    # Common HTTP features.
    "django.middleware.common.CommonMiddleware",

    # CSRF protection.
    "django.middleware.csrf.CsrfViewMiddleware",

    # Authentication.
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Django messages framework.
    "django.contrib.messages.middleware.MessageMiddleware",

    # Prevent clickjacking attacks.
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==========================================================
# STATIC FILES
# ==========================================================

# URL used for serving static files.
STATIC_URL = "/static/"

# Folder where collectstatic stores all static files.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Storage backends.
STORAGES = {

    # User uploaded media stored in Cloudinary.
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },

    # Static CSS/JS/images served using WhiteNoise.
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ==========================================================
# CORS
# ==========================================================

# Don't allow every website to access your API.
CORS_ALLOW_ALL_ORIGINS = False

# Allow only these frontend applications.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://lifehub-teal.vercel.app",
]

# ==========================================================
# CLOUDINARY
# ==========================================================

# Configure Cloudinary using environment variables.
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# ==========================================================
# EMAIL
# ==========================================================

# Email credentials.
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# ==========================================================
# PRODUCTION SECURITY
# ==========================================================

# Force HTTPS.
SECURE_SSL_REDIRECT = True

# Session cookies only over HTTPS.
SESSION_COOKIE_SECURE = True

# CSRF cookies only over HTTPS.
CSRF_COOKIE_SECURE = True

# Tell Django that Render terminates SSL.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

# Use forwarded host from proxy.
USE_X_FORWARDED_HOST = True

# Enable HTTP Strict Transport Security.
SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

# Prevent clickjacking.
X_FRAME_OPTIONS = "DENY"

# Prevent MIME sniffing.
SECURE_CONTENT_TYPE_NOSNIFF = True

# Referrer policy.
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ==========================================================
# LOGGING
# ==========================================================

# Print detailed errors to Render logs.
LOGGING = {
    "version": 1,

    # Keep Django's default loggers.
    "disable_existing_loggers": False,

    # Log format.
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },

    # Output logs to console.
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },

    # Django logs.
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },

        # Database related errors.
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },

    # Root logger.
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}
