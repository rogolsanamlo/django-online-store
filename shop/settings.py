"""
Django settings for the shop project.

All secrets / environment-specific values are read from environment
variables (see ``.env.example``). Nothing sensitive is stored in the repo.
"""
import os
import sys
from pathlib import Path

from django.contrib.messages import constants as message_constants

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a local ``.env`` file when python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv(BASE_DIR / ".env")
except ImportError:  # optional dependency
    pass


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        # Only for local development. Never used when DEBUG is False.
        SECRET_KEY = "django-insecure-dev-only-key-change-me"
    else:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DEBUG is False.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost" if DEBUG else "")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # local apps
    "apps.main.apps.MainConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.products.apps.ProductsConfig",
    "apps.discounts.apps.DiscountsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.warehouses.apps.WarehousesConfig",
    "apps.comment_scoring_favorites.apps.CommentScoringFavoritesConfig",
    "apps.search.apps.SearchConfig",
    "apps.orders.apps.OrdersConfig",
    # third party
    "django_admin_listfilter_dropdown",
    "ckeditor",
    "ckeditor_uploader",
    "django_render_partial",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "middlewares.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.main.views.media_admin",
            ],
        },
    },
]

WSGI_APPLICATION = "shop.wsgi.application"

# ---------------------------------------------------------------------------
# Database
#   default          -> MySQL (needs `mysqlclient` and an existing empty database)
#   DB_ENGINE=sqlite -> SQLite file db.sqlite3 (handy for a quick local try-out)
# ---------------------------------------------------------------------------
if os.environ.get("DB_ENGINE", "mysql").lower() == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("DB_NAME", "dbshop"),
            "USER": os.environ.get("DB_USER", "root"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_URL = "accounts:login"

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fa"
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
# The code base compares naive ``datetime.now()`` values with DB values
# (discount baskets, coupons), so aware datetimes are intentionally disabled.
USE_TZ = False

# ---------------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Make Django message levels match Bootstrap alert classes (alert-danger ...)
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# ---------------------------------------------------------------------------
# CKEditor
# ---------------------------------------------------------------------------
CKEDITOR_UPLOAD_PATH = "images/ckeditor/upload_files/"
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_STORAGE_BACKEND = "django.core.files.storage.FileSystemStorage"

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [["Bold", "Link", "Unlink", "Image"]],
    },
    "special": {
        "toolbar": "Special",
        "height": 500,
        "toolbar_Special": [["Bold", "Link", "Unlink", "Image"], ["CodeSnippet"]],
        "extraPlugins": ",".join(["codesnippet", "clipboard"]),
    },
    "special_an": {
        "toolbar": "Special",
        "height": 500,
        "toolbar_Special": [["Bold"], ["CodeSnippet"]],
        "extraPlugins": ",".join(["codesnippet"]),
    },
}

# ---------------------------------------------------------------------------
# SMS (Kavenegar)
# ---------------------------------------------------------------------------
KAVENEGAR_API_KEY = os.environ.get("KAVENEGAR_API_KEY", "")
KAVENEGAR_SENDER = os.environ.get("KAVENEGAR_SENDER", "")

# ---------------------------------------------------------------------------
# ZarinPal
#   ZARINPAL_SANDBOX=True  -> sandbox gateway (safe for development/demo)
# ---------------------------------------------------------------------------
ZARINPAL_MERCHANT_ID = os.environ.get(
    "ZARINPAL_MERCHANT_ID", "00000000-0000-0000-0000-000000000000"
)
ZARINPAL_SANDBOX = env_bool("ZARINPAL_SANDBOX", True)

# ---------------------------------------------------------------------------
# Production hardening
# ---------------------------------------------------------------------------
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Fast password hashing while running the test suite (PBKDF2 makes tests very slow)
if "test" in sys.argv:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
