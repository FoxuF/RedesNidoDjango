"""
Django settings for IIS deployment
"""
from RedesDjango.shared_settings import *

DEBUG = False

ALLOWED_HOSTS = [
    "172.25.4.46",
    ".academic",
    ".academic.mixcoac.upmx.mx",
    ".localhost",
    "127.0.0.1",
]

# static files
STATIC_URL = 'static/'
# noinspection PyUnresolvedReferences
STATIC_ROOT = BASE_DIR / "static"

# secrets
SECRET_KEY = iniParser.get('SECRETS', 'SECRET_KEY')

# Database
# local mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': str(SECRETS_DIR / "djangodb.cnf"),
            "autocommit": True,
        }
    }
}

# Production Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'redes_django_cache',
    }
}
