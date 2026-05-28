"""
Django settings for teba project - OPTIMIZED FOR LOCAL DEVELOPMENT
(FRENCH REMOVED - ENGLISH ONLY)
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

# FORCE LOCAL DEVELOPMENT
IS_PRODUCTION = False
IS_RAILWAY = False
DEBUG = True  # MUST BE TRUE FOR LOCAL

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-only-for-local-development-change-in-production')

# Local development hosts
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
    # 'rosetta',  # REMOVED - No longer needed (was for translations)
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',  # REMOVED - No translations needed
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
                # 'django.template.context_processors.i18n',  # REMOVED - No translations
                'core.context_processors.user_locations',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'teba.wsgi.application'

# =======================
# DATABASE - Force SQLite for Local
# =======================

# =======================
# DATABASE - PostgreSQL for Railway
# =======================

import dj_database_url

# Railway PostgreSQL connection string
DATABASE_URL = 'postgresql://postgres:cSGoxJEywsZbMqWEkmcDtqRpwUWQBihM@zephyr.proxy.rlwy.net:19136/railway'

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
    )
}

# Add SSL requirement for secure connection
DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
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

# Force English only
LANGUAGE_CODE = 'en-us'

# Single language only - English
LANGUAGES = [
    ('en', 'English'),
]

# Disable internationalization completely
USE_I18N = False
USE_L10N = False

# Timezone settings
TIME_ZONE = 'Africa/Kampala'  # Uganda timezone
USE_TZ = True

# Number formatting
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3

# Remove locale paths (not needed)
# LOCALE_PATHS = [BASE_DIR / 'locale']  # REMOVED

# =======================
# STATIC FILES
# =======================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'core' / 'static',
]

# Use simple static storage for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

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

# LOCAL DEVELOPMENT - All security disabled
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

AXES_ENABLED = False  # Disable for development
AXES_FAILURE_LIMIT = 100
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'account/lockout.html'

# =======================
# ALLAUTH CONFIGURATION - USERNAME LOGIN
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
# EMAIL CONFIGURATION - Console for Development
# =======================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
DEFAULT_FROM_EMAIL = 'dev@tusakimu.com'  # Updated company name

# =======================
# SITE CONFIGURATION
# =======================

SITE_NAME = "Tusakimu Enterprises Inventory Management"  # Updated company name
SITE_DOMAIN = "http://localhost:8000"
SUPPORT_EMAIL = 'support@tusakimu.com'  # Updated email
ADMIN_EMAIL = 'admin@tusakimu.com'  # Updated email

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# ADDITIONAL FIXES FOR JAVASCRIPT
# =======================

# Fix MIME types for JavaScript
import mimetypes
mimetypes.add_type("application/javascript", ".js", True)

# Disable any content security policy
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# =======================
# REMOVE ROSETTA URLS
# =======================
# Note: Remove 'rosetta/' from your main urls.py as well

# =======================
# DEBUG OUTPUT
# =======================

print("=" * 50)
print("TUSAKIMU ENTERPRISES - LOCAL DEVELOPMENT SETTINGS")
print("=" * 50)
print(f"Debug Mode: {DEBUG}")
print(f"Language: ENGLISH ONLY (French Removed)")
print(f"Database: {DATABASES['default']['ENGINE']}")
print(f"Static Files: Development mode")
print(f"Security Headers: DISABLED for development")
print("=" * 50)