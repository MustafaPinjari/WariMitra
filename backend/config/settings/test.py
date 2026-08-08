"""Minimal test settings for WariMitra - no DB, no GIS, no external services needed"""
from .base import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable GIS apps that require GDAL (not available in local test env)
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'gis' not in app]

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''

# Turn off debug toolbar and extensions for tests
INSTALLED_APPS = [
    app for app in INSTALLED_APPS
    if app not in ('debug_toolbar', 'django_extensions')
]

MIDDLEWARE = [
    m for m in MIDDLEWARE
    if 'debug_toolbar' not in m
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
