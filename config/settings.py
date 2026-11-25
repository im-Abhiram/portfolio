"""
Django settings for Abhiram Anil Portfolio project.
Optimized for local development and free PythonAnywhere deployment.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file if present (never committed to git)
try:
    from dotenv import load_dotenv
    _env_file = BASE_DIR / '.env'
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass

# Security settings
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'c9b84f3e6a1d7e2f5b8c0a9d3e7f1b5c8e2a4d6f0b9c3e7a1d5f8b2c4e6a0d9f'
)

# DEBUG is True by default in local dev, set to 'False' on PythonAnywhere
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').strip().lower() in ('true', '1', 'yes')

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

# Max upload size: 10MB to protect PythonAnywhere storage
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Security Headers & Cookies
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # Allows JS to read csrftoken cookie for AJAX if needed
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 1 day

# Production SSL / HTTPS hardening when DEBUG is False
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
