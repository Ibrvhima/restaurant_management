"""
PostgreSQL settings for Render deployment.
"""

import os
from decouple import config
from .settings import *

# SECURITY
DEBUG = False
ALLOWED_HOSTS = ['*']

# DATABASE - PostgreSQL pour Render
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
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

# SESSIONS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
