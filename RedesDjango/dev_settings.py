"""
Django settings for development
"""
from RedesDjango.shared_settings import *

DEBUG = True

SECRET_KEY = 'django-insecure-j_c9jd5t7*)ex1p4cg5=2vl04s1@y_iq-gr+zn=2cagwk8)v$t'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# dev cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ldap debug logger
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}

# debug static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'staticfiles',
]
