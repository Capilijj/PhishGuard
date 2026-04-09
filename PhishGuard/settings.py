"""
Django settings for PhishGuard project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-_____95w(zbn@1p&37ap+20!l_j*n4$^elqv7+efk&%60p5@8*'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# ── Applications ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # PhishGuard apps
    'homepage',
    'admin_panel',
]

# ── Middleware ─────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PhishGuard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PhishGuard.wsgi.application'


# ── Database — SQL Server ──────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": "PhishGuard",
        "USER": "",
        "PASSWORD": "",
        "HOST": "DESKTOP-LSU5CF3\\SQLEXPRESS",
        "PORT": "",
        "OPTIONS": {
            "driver": "ODBC Driver 18 for SQL Server",
            "extra_params": "Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=yes",
        },
    },
}


# ── Internationalization ───────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True


# ── Static files ───────────────────────────────────────────────
STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


# ── Media files ────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ── Session ────────────────────────────────────────────────────
SESSION_ENGINE               = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE           = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ── Security ───────────────────────────────────────────────────
SESSION_COOKIE_SECURE       = False
CSRF_COOKIE_SECURE          = False
SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# ── Email — Gmail SMTP ─────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = f'PhishGuard <{os.getenv("EMAIL_HOST_USER")}>'