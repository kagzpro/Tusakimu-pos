"""
Django settings for teba project - OPTIMIZED FOR LOCAL DEVELOPMENT & RAILWAY
(ENGLISH ONLY)
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# =======================
# BASE & ENVIRONMENT
# =======================

BASE_DIR = Path(__file__).resolve().parent.parent

# Detect if running on Railway
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') == 'production' or 'DATABASE_URL' in os.environ
IS_PRODUCTION = IS_RAILWAY
DEBUG = not IS_PRODUCTION  # False on Railway, True locally

# Secret Key - use environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-only-for-local-development-change-in-production')

# Allowed hosts
if IS_RAILWAY:
    ALLOWED_HOSTS = ['*', '.railway.app', 'tusakimu-pos.up.railway.app']
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://tusakimu-pos.up.railway.app',
    ]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://0.0.0.0:8000',
    ]

# =======================
# INSTALLED APPS
# =======================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'whitenoise.runserver_nostatic',  # Add whitenoise for static files
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'axes',

    'core',
    'transactions',
    'inventory',
]

# =======================
# MIDDLEWARE
# =======================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise - IMPORTANT: after security, before others
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',

    'core.middleware.SessionErrorMiddleware',
    'core.middleware.LocationAccessMiddleware',
]

ROOT_URLCONF = 'teba.urls'

# =======================
# TEMPLATES
# =======================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_locations',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'teba.wsgi.application'

# =======================
# DATABASE - PostgreSQL for Railway, SQLite for Local
# =======================

if IS_RAILWAY:
    # Use Railway PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Use SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =======================
# PASSWORD VALIDATION
# =======================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
]

# =======================
# INTERNATIONALIZATION - ENGLISH ONLY
# =======================

LANGUAGE_CODE = 'en-us'
LANGUAGES = [('en', 'English')]
USE_I18N = False
USE_L10N = False
TIME_ZONE = 'Africa/Kampala'
USE_TZ = True

# Number formatting
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3

# =======================
# STATIC FILES
# =======================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'core' / 'static',
]

# Use whitenoise for static files in production
if IS_RAILWAY:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =======================
# MEDIA FILES
# =======================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =======================
# AUTHENTICATION
# =======================

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_SAVE_EVERY_REQUEST = True

# Security settings - different for development vs production
if IS_RAILWAY:
    # Production security settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Development security settings (disabled)
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# =======================
# AXES - Disabled for Development
# =======================

AXES_ENABLED = not IS_RAILWAY  # Disable for local, enable for production
AXES_FAILURE_LIMIT = 5
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'account/lockout.html'

# =======================
# ALLAUTH CONFIGURATION
# =======================

SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*']
ACCOUNT_ADAPTER = 'core.adapters.CustomAccountAdapter'
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False

LOGIN_REDIRECT_URL = '/inventory/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# =======================
# EMAIL CONFIGURATION
# =======================

if IS_RAILWAY:
    # Use console email for Railway (you can later configure SMTP)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'noreply@tusakimu.com'

# =======================
# SITE CONFIGURATION
# =======================

if IS_RAILWAY:
    SITE_NAME = "Tusakimu Enterprises Inventory Management"
    SITE_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'https://tusakimu-pos.up.railway.app')
else:
    SITE_NAME = "Tusakimu Enterprises Inventory Management (Development)"
    SITE_DOMAIN = "http://localhost:8000"

SUPPORT_EMAIL = 'support@tusakimu.com'
ADMIN_EMAIL = 'admin@tusakimu.com'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# ADDITIONAL FIXES FOR JAVASCRIPT
# =======================

import mimetypes
mimetypes.add_type("application/javascript", ".js", True)
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# =======================
# LOGGING (Optional - for debugging production)
# =======================

if IS_RAILWAY:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            },
        },
    }

# =======================
# DEBUG OUTPUT
# =======================

print("=" * 50)
print("TUSAKIMU ENTERPRISES - SETTINGS LOADED")
print("=" * 50)
print(f"Environment: {'RAILWAY (Production)' if IS_RAILWAY else 'LOCAL (Development)'}")
print(f"Debug Mode: {DEBUG}")
print(f"Database: {DATABASES['default']['ENGINE']}")
print(f"Static Files: {'Whitenoise (Production)' if IS_RAILWAY else 'Development mode'}")
print(f"Security Headers: {'ENABLED' if IS_RAILWAY else 'DISABLED for development'}")
print("=" * 50)