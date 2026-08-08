"""Production settings for WariMitra"""
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['warimitra.example.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
