"""
Production settings for Django project.

These settings override the base settings for production deployment.
"""

import os
from decouple import config
from .settings import *

# SECURITY
DEBUG = False
ALLOWED_HOSTS = ['*']  # Render gère automatiquement les domaines

# DATABASE - PostgreSQL pour Render
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# STATIC FILES
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# MIDDLEWARE
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# SECURITY SETTINGS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# SESSIONS - Adapté pour Render
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
