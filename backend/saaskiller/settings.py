from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-do-not-use-in-production")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]

# ── Apps ──────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "anymail",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # === FEATURE: github-oauth ===
    "allauth.socialaccount.providers.github",
    # === END FEATURE: github-oauth ===
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "drf_spectacular",
    # Local
    "users",
    # === FEATURE: workspaces ===
    "workspaces",
    # === END FEATURE: workspaces ===
    # === FEATURE: tasks ===
    "django_q",
    "tasks",
    # === END FEATURE: tasks ===
    # === FEATURE: websockets ===
    "channels",
    "realtime",
    # === END FEATURE: websockets ===
    # === FEATURE: stripe ===
    "billing",
    # === END FEATURE: stripe ===
    # === FEATURE: apikeys ===
    "apikeys",
    # === END FEATURE: apikeys ===
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "saaskiller.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "saaskiller.wsgi.application"
ASGI_APPLICATION = "saaskiller.asgi.application"

# ── Database ──────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=0)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Auth ──────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ── REST Framework ────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # === FEATURE: apikeys ===
        "apikeys.authentication.ApiKeyAuthentication",
        # === END FEATURE: apikeys ===
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "signup": "5/hour",
        "magic_link": "5/hour",
        "login": "10/hour",
        "resend_verification": "5/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ── allauth / OAuth2 ──────────────────────────────────────────────────────────

ACCOUNT_ADAPTER = "users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "users.adapters.SocialAccountAdapter"

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*"]
ACCOUNT_EMAIL_VERIFICATION = "none"  # We handle verification ourselves

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        },
    },
    # === FEATURE: github-oauth ===
    "github": {
        "SCOPE": ["user:email"],
        "APP": {
            "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
            "secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        },
    },
    # === END FEATURE: github-oauth ===
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_RETURN_EXPIRATION": False,
    "USER_DETAILS_SERIALIZER": "users.serializers.UserSerializer",
}

# ── CORS ──────────────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5175,http://127.0.0.1:5175"
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

# ── HTTPS / Proxy (production only) ───────────────────────────────────────────
# deplo.io and PythonAnywhere both terminate TLS at their proxy layer.
# These settings are safe to enable unconditionally when DEBUG=False.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [o for o in CORS_ALLOWED_ORIGINS if o.startswith("https")]

# ── Email ─────────────────────────────────────────────────────────────────────

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "SaasKiller <noreply@example.com>")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
if RESEND_API_KEY:
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
    ANYMAIL = {"RESEND_API_KEY": RESEND_API_KEY}
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Internationalisation ──────────────────────────────────────────────────────

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Zurich"
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── OpenAPI ────────────────────────────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    "TITLE": "SaasKiller API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# === FEATURE: tasks ===
Q_CLUSTER = {
    "name": "saaskiller",
    "workers": 2,
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}
# === END FEATURE: tasks ===

# === FEATURE: websockets ===
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"  # use Redis in prod via env
    }
}
# === END FEATURE: websockets ===

# === FEATURE: s3 ===
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "https://s3.ch-dk-2.bintra.cloud")
AWS_S3_REGION_NAME = "ch-dk-2"
AWS_DEFAULT_ACL = None
if AWS_ACCESS_KEY_ID:
    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}
# === END FEATURE: s3 ===

# === FEATURE: sentry ===
import sentry_sdk
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "development"),
    )
# === END FEATURE: sentry ===

# === FEATURE: stripe ===
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID_MONTHLY = os.getenv("STRIPE_PRICE_ID_MONTHLY", "")
STRIPE_PRICE_ID_YEARLY = os.getenv("STRIPE_PRICE_ID_YEARLY", "")
# === END FEATURE: stripe ===
