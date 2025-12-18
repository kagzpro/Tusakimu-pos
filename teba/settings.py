"""
Django settings for teba project - OPTIMIZED FOR RAILWAY & SINGLE EMAIL + USERNAME LOGIN
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

IS_RAILWAY = os.getenv('RAILWAY_ENVIRONMENT') is not None
IS_PRODUCTION = IS_RAILWAY or os.getenv('DJANGO_ENV') == 'production'

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise Exception("SECRET_KEY must be set in production!")
    else:
        SECRET_KEY = 'dev-key-only-for-local-development-change-in-production'

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true' and not IS_PRODUCTION

if IS_RAILWAY:
    railway_domain = os.getenv('RAILWAY_STATIC_URL', 'your-app.up.railway.app')
    ALLOWED_HOSTS = [railway_domain, 'localhost', '127.0.0.1', '0.0.0.0']
    CSRF_TRUSTED_ORIGINS = [f"https://{railway_domain}"]
else:
    ALLOWED_HOSTS = ['*']
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
    'rosetta',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
                'django.template.context_processors.i18n',
                'core.context_processors.user_locations',
            ],
        },
    },
]

WSGI_APPLICATION = 'teba.wsgi.application'

# =======================
# DATABASE
# =======================

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
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
# INTERNATIONALIZATION
# =======================

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = ' '
NUMBER_GROUPING = 3

# =======================
# STATIC FILES
# =======================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_HTTPONLY = False

if IS_PRODUCTION:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    LANGUAGE_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    LANGUAGE_COOKIE_SECURE = False

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# =======================
# AXES
# =======================

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = 'account/lockout.html'
AXES_NEVER_LOCKOUT_WHITELIST = [
    '/core/verify-login/',
    '/core/verify-email-signup/',
    '/core/session-test/',
]

# =======================
# ALLAUTH CONFIGURATION - USERNAME LOGIN
# =======================

SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD ="username"
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
# EMAIL CONFIGURATION - SINGLE STATIC EMAIL
# =======================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('SYSTEM_EMAIL', 'tebaspprt@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# =======================
# SITE CONFIGURATION
# =======================

SITE_NAME = "Teba Paint Center"
if IS_RAILWAY:
    SITE_DOMAIN = f"https://{os.getenv('RAILWAY_STATIC_URL', 'your-app.up.railway.app')}"
else:
    SITE_DOMAIN = "http://localhost:8000"

SUPPORT_EMAIL = 'tebaspprt@gmail.com'
ADMIN_EMAIL = 'tebaspprt@gmail.com'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# DEBUG OUTPUT
# =======================

print(f"=== Teba Settings Loaded ===")
print(f"Environment: {'PRODUCTION' if IS_PRODUCTION else 'DEVELOPMENT'}")
print(f"Debug: {DEBUG}")
print(f"Domain: {SITE_DOMAIN}")
print(f"Email Backend: {EMAIL_BACKEND}")
print(f"Available Languages: {[lang[0] for lang in LANGUAGES]}")
print("=============================")
