"""
Django settings for Abhiram Anil Portfolio project.
Optimized for local development and free PythonAnywhere deployment.
"""

from pathlib import Path
import os
import secrets

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file if present (never committed to git)
try:
    from dotenv import load_dotenv
    _env_file = BASE_DIR / '.env'
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass


def _resolve_secret_key() -> str:
    """
    Loads DJANGO_SECRET_KEY from environment variables.
    If unset, loads or generates a local per-host CSPRNG secret stored in
    a gitignored file (.django_secret_key) so no hardcoded key exists in Git.
    """
    env_key = os.environ.get('DJANGO_SECRET_KEY', '').strip()
    if env_key:
        return env_key

    secret_file = BASE_DIR / '.django_secret_key'
    if secret_file.exists():
        stored = secret_file.read_text(encoding='utf-8').strip()
        if len(stored) >= 50:
            return stored

    generated = secrets.token_urlsafe(64)
    try:
        secret_file.write_text(generated, encoding='utf-8')
        if os.name == 'posix':
            os.chmod(secret_file, 0o600)
    except OSError:
        pass
    return generated


# Security settings
SECRET_KEY = _resolve_secret_key()

# DEBUG is True by default in local dev, set to 'False' on PythonAnywhere
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').strip().lower() in ('true', '1', 'yes')

# Only trust X-Forwarded-For / X-Real-IP when running behind a configured reverse proxy
TRUST_PROXY_HEADERS = os.environ.get('DJANGO_TRUST_PROXY_HEADERS', 'False').strip().lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost,.pythonanywhere.com,abhiramportfolio.pythonanywhere.com'
).split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'https://abhiramportfolio.pythonanywhere.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom Portfolio Apps
    'core.apps.CoreConfig',
    'portfolio.apps.PortfolioConfig',
    'lab.apps.LabConfig',
    'journal.apps.JournalConfig',
    'contact.apps.ContactConfig',
    'portal.apps.PortalConfig',
    'nexus.apps.NexusConfig',
    'intelligence.apps.IntelligenceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'core.context_processors.global_portfolio_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database: SQLite3 only for lightweight, zero-maintenance PythonAnywhere free hosting
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for static asset serving on PythonAnywhere without requiring a CDN
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files (Resumes, Project screenshots, Certifications)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Max upload sizes to protect PythonAnywhere storage and memory
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# Security Headers & Cookies
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 28800  # 8 hours

# Production SSL / HTTPS hardening when DEBUG is False
if not DEBUG:
    _behind_ssl_proxy = os.environ.get('DJANGO_BEHIND_HTTPS_PROXY', 'True').strip().lower() in ('true', '1', 'yes')
    if _behind_ssl_proxy:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'True').strip().lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Lightweight Security & Operational Logging (PythonAnywhere disk-safe rotating logs)
_LOG_DIR = BASE_DIR / 'logs'
try:
    _LOG_DIR.mkdir(exist_ok=True)
    _HAS_LOG_DIR = True
except OSError:
    _HAS_LOG_DIR = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security_fmt': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'security_fmt',
        },
        **({
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(_LOG_DIR / 'security.log'),
                'maxBytes': 1024 * 1024,  # 1 MB cap
                'backupCount': 3,
                'formatter': 'security_fmt',
                'encoding': 'utf-8',
            },
        } if _HAS_LOG_DIR else {}),
    },
    'loggers': {
        'security': {
            'handlers': ['console', 'security_file'] if _HAS_LOG_DIR else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'] if _HAS_LOG_DIR else ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
