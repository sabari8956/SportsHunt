from .common import *
import os

from dotenv import load_dotenv
load_dotenv()

DEBUG = False if os.environ.get("DEBUG") == 'False' else True
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(' ')
print(ALLOWED_HOSTS)

# Database  [ dev will use sqlite3 / prod will be mysql ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files conf
STATIC_URL = 'static/'
MEDIA_URL = 'media/'



STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'media'),
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email'
        ],
        "AUTH_PARAMS": {"access_type": "online"}
    }
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("OTP_MAIL_ADDRESS")
EMAIL_HOST_PASSWORD = os.environ.get("OTP_MAIL_PASSWORD")

# Azure Blob Storage settings
AZURE_ACCOUNT_NAME = os.environ.get("STORAGE_BUCKET_NAME")
AZURE_ACCOUNT_KEY = os.environ.get("STORAGE_BUCKET_KEY")
AZURE_CONTAINER = os.environ.get("STORAGE_BUCKET_CONTAINER")

print(AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_CONTAINER)
# Use Azure Blob Storage for media files
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_CUSTOM_DOMAIN = f'{AZURE_ACCOUNT_NAME}.blob.core.windows.net'
MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_CONTAINER}/'

